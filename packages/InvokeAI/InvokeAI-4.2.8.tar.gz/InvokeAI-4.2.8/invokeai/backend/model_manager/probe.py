import json
import re
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

import safetensors.torch
import spandrel
import torch
from picklescan.scanner import scan_file_path

import invokeai.backend.util.logging as logger
from invokeai.app.util.misc import uuid_string
from invokeai.backend.model_hash.model_hash import HASHING_ALGORITHMS, ModelHash
from invokeai.backend.model_manager.config import (
    AnyModelConfig,
    BaseModelType,
    ControlAdapterDefaultSettings,
    InvalidModelConfigException,
    MainModelDefaultSettings,
    ModelConfigFactory,
    ModelFormat,
    ModelRepoVariant,
    ModelSourceType,
    ModelType,
    ModelVariantType,
    SchedulerPredictionType,
)
from invokeai.backend.model_manager.util.model_util import lora_token_vector_length, read_checkpoint_meta
from invokeai.backend.spandrel_image_to_image_model import SpandrelImageToImageModel
from invokeai.backend.util.silence_warnings import SilenceWarnings

CkptType = Dict[str | int, Any]

LEGACY_CONFIGS: Dict[BaseModelType, Dict[ModelVariantType, Union[str, Dict[SchedulerPredictionType, str]]]] = {
    BaseModelType.StableDiffusion1: {
        ModelVariantType.Normal: {
            SchedulerPredictionType.Epsilon: "v1-inference.yaml",
            SchedulerPredictionType.VPrediction: "v1-inference-v.yaml",
        },
        ModelVariantType.Inpaint: "v1-inpainting-inference.yaml",
    },
    BaseModelType.StableDiffusion2: {
        ModelVariantType.Normal: {
            SchedulerPredictionType.Epsilon: "v2-inference.yaml",
            SchedulerPredictionType.VPrediction: "v2-inference-v.yaml",
        },
        ModelVariantType.Inpaint: {
            SchedulerPredictionType.Epsilon: "v2-inpainting-inference.yaml",
            SchedulerPredictionType.VPrediction: "v2-inpainting-inference-v.yaml",
        },
        ModelVariantType.Depth: "v2-midas-inference.yaml",
    },
    BaseModelType.StableDiffusionXL: {
        ModelVariantType.Normal: "sd_xl_base.yaml",
        ModelVariantType.Inpaint: "sd_xl_inpaint.yaml",
    },
    BaseModelType.StableDiffusionXLRefiner: {
        ModelVariantType.Normal: "sd_xl_refiner.yaml",
    },
}


class ProbeBase(object):
    """Base class for probes."""

    def __init__(self, model_path: Path):
        self.model_path = model_path

    def get_base_type(self) -> BaseModelType:
        """Get model base type."""
        raise NotImplementedError

    def get_format(self) -> ModelFormat:
        """Get model file format."""
        raise NotImplementedError

    def get_variant_type(self) -> Optional[ModelVariantType]:
        """Get model variant type."""
        return None

    def get_scheduler_prediction_type(self) -> Optional[SchedulerPredictionType]:
        """Get model scheduler prediction type."""
        return None

    def get_image_encoder_model_id(self) -> Optional[str]:
        """Get image encoder (IP adapters only)."""
        return None


class ModelProbe(object):
    PROBES: Dict[str, Dict[ModelType, type[ProbeBase]]] = {
        "diffusers": {},
        "checkpoint": {},
        "onnx": {},
    }

    CLASS2TYPE = {
        "StableDiffusionPipeline": ModelType.Main,
        "StableDiffusionInpaintPipeline": ModelType.Main,
        "StableDiffusionXLPipeline": ModelType.Main,
        "StableDiffusionXLImg2ImgPipeline": ModelType.Main,
        "StableDiffusionXLInpaintPipeline": ModelType.Main,
        "LatentConsistencyModelPipeline": ModelType.Main,
        "AutoencoderKL": ModelType.VAE,
        "AutoencoderTiny": ModelType.VAE,
        "ControlNetModel": ModelType.ControlNet,
        "CLIPVisionModelWithProjection": ModelType.CLIPVision,
        "T2IAdapter": ModelType.T2IAdapter,
    }

    @classmethod
    def register_probe(
        cls, format: Literal["diffusers", "checkpoint", "onnx"], model_type: ModelType, probe_class: type[ProbeBase]
    ) -> None:
        cls.PROBES[format][model_type] = probe_class

    @classmethod
    def probe(
        cls, model_path: Path, fields: Optional[Dict[str, Any]] = None, hash_algo: HASHING_ALGORITHMS = "blake3_single"
    ) -> AnyModelConfig:
        """
        Probe the model at model_path and return its configuration record.

        :param model_path: Path to the model file (checkpoint) or directory (diffusers).
        :param fields: An optional dictionary that can be used to override probed
        fields. Typically used for fields that don't probe well, such as prediction_type.

        Returns: The appropriate model configuration derived from ModelConfigBase.
        """
        if fields is None:
            fields = {}

        model_path = model_path.resolve()

        format_type = ModelFormat.Diffusers if model_path.is_dir() else ModelFormat.Checkpoint
        model_info = None
        model_type = ModelType(fields["type"]) if "type" in fields and fields["type"] else None
        if not model_type:
            if format_type is ModelFormat.Diffusers:
                model_type = cls.get_model_type_from_folder(model_path)
            else:
                model_type = cls.get_model_type_from_checkpoint(model_path)
        format_type = ModelFormat.ONNX if model_type == ModelType.ONNX else format_type

        probe_class = cls.PROBES[format_type].get(model_type)
        if not probe_class:
            raise InvalidModelConfigException(f"Unhandled combination of {format_type} and {model_type}")

        probe = probe_class(model_path)

        fields["source_type"] = fields.get("source_type") or ModelSourceType.Path
        fields["source"] = fields.get("source") or model_path.as_posix()
        fields["key"] = fields.get("key", uuid_string())
        fields["path"] = model_path.as_posix()
        fields["type"] = fields.get("type") or model_type
        fields["base"] = fields.get("base") or probe.get_base_type()
        fields["variant"] = fields.get("variant") or probe.get_variant_type()
        fields["prediction_type"] = fields.get("prediction_type") or probe.get_scheduler_prediction_type()
        fields["image_encoder_model_id"] = fields.get("image_encoder_model_id") or probe.get_image_encoder_model_id()
        fields["name"] = fields.get("name") or cls.get_model_name(model_path)
        fields["description"] = (
            fields.get("description") or f"{fields['base'].value} {model_type.value} model {fields['name']}"
        )
        fields["format"] = fields.get("format") or probe.get_format()
        fields["hash"] = fields.get("hash") or ModelHash(algorithm=hash_algo).hash(model_path)

        fields["default_settings"] = fields.get("default_settings")

        if not fields["default_settings"]:
            if fields["type"] in {ModelType.ControlNet, ModelType.T2IAdapter}:
                fields["default_settings"] = get_default_settings_controlnet_t2i_adapter(fields["name"])
            elif fields["type"] is ModelType.Main:
                fields["default_settings"] = get_default_settings_main(fields["base"])

        if format_type == ModelFormat.Diffusers and isinstance(probe, FolderProbeBase):
            fields["repo_variant"] = fields.get("repo_variant") or probe.get_repo_variant()

        # additional fields needed for main and controlnet models
        if (
            fields["type"] in [ModelType.Main, ModelType.ControlNet, ModelType.VAE]
            and fields["format"] is ModelFormat.Checkpoint
        ):
            ckpt_config_path = cls._get_checkpoint_config_path(
                model_path,
                model_type=fields["type"],
                base_type=fields["base"],
                variant_type=fields["variant"],
                prediction_type=fields["prediction_type"],
            )
            fields["config_path"] = str(ckpt_config_path)

        # additional fields needed for main non-checkpoint models
        elif fields["type"] == ModelType.Main and fields["format"] in [
            ModelFormat.ONNX,
            ModelFormat.Olive,
            ModelFormat.Diffusers,
        ]:
            fields["upcast_attention"] = fields.get("upcast_attention") or (
                fields["base"] == BaseModelType.StableDiffusion2
                and fields["prediction_type"] == SchedulerPredictionType.VPrediction
            )

        model_info = ModelConfigFactory.make_config(fields)  # , key=fields.get("key", None))
        return model_info

    @classmethod
    def get_model_name(cls, model_path: Path) -> str:
        if model_path.suffix in {".safetensors", ".bin", ".pt", ".ckpt"}:
            return model_path.stem
        else:
            return model_path.name

    @classmethod
    def get_model_type_from_checkpoint(cls, model_path: Path, checkpoint: Optional[CkptType] = None) -> ModelType:
        if model_path.suffix not in (".bin", ".pt", ".ckpt", ".safetensors", ".pth"):
            raise InvalidModelConfigException(f"{model_path}: unrecognized suffix")

        if model_path.name == "learned_embeds.bin":
            return ModelType.TextualInversion

        ckpt = checkpoint if checkpoint else read_checkpoint_meta(model_path, scan=True)
        ckpt = ckpt.get("state_dict", ckpt)

        for key in [str(k) for k in ckpt.keys()]:
            if key.startswith(("cond_stage_model.", "first_stage_model.", "model.diffusion_model.")):
                return ModelType.Main
            elif key.startswith(("encoder.conv_in", "decoder.conv_in")):
                return ModelType.VAE
            elif key.startswith(("lora_te_", "lora_unet_")):
                return ModelType.LoRA
            elif key.endswith(("to_k_lora.up.weight", "to_q_lora.down.weight")):
                return ModelType.LoRA
            elif key.startswith(("controlnet", "control_model", "input_blocks")):
                return ModelType.ControlNet
            elif key.startswith(("image_proj.", "ip_adapter.")):
                return ModelType.IPAdapter
            elif key in {"emb_params", "string_to_param"}:
                return ModelType.TextualInversion

        # diffusers-ti
        if len(ckpt) < 10 and all(isinstance(v, torch.Tensor) for v in ckpt.values()):
            return ModelType.TextualInversion

        # Check if the model can be loaded as a SpandrelImageToImageModel.
        # This check is intentionally performed last, as it can be expensive (it requires loading the model from disk).
        try:
            # It would be nice to avoid having to load the Spandrel model from disk here. A couple of options were
            # explored to avoid this:
            # 1. Call `SpandrelImageToImageModel.load_from_state_dict(ckpt)`, where `ckpt` is a state_dict on the meta
            #    device. Unfortunately, some Spandrel models perform operations during initialization that are not
            #    supported on meta tensors.
            # 2. Spandrel has internal logic to determine a model's type from its state_dict before loading the model.
            #    This logic is not exposed in spandrel's public API. We could copy the logic here, but then we have to
            #    maintain it, and the risk of false positive detections is higher.
            SpandrelImageToImageModel.load_from_file(model_path)
            return ModelType.SpandrelImageToImage
        except spandrel.UnsupportedModelError:
            pass
        except RuntimeError as e:
            if "No such file or directory" in str(e):
                # This error is expected if the model_path does not exist (which is the case in some unit tests).
                pass
            else:
                raise e

        raise InvalidModelConfigException(f"Unable to determine model type for {model_path}")

    @classmethod
    def get_model_type_from_folder(cls, folder_path: Path) -> ModelType:
        """Get the model type of a hugging-face style folder."""
        class_name = None
        error_hint = None
        for suffix in ["bin", "safetensors"]:
            if (folder_path / f"learned_embeds.{suffix}").exists():
                return ModelType.TextualInversion
            if (folder_path / f"pytorch_lora_weights.{suffix}").exists():
                return ModelType.LoRA
        if (folder_path / "unet/model.onnx").exists():
            return ModelType.ONNX
        if (folder_path / "image_encoder.txt").exists():
            return ModelType.IPAdapter

        i = folder_path / "model_index.json"
        c = folder_path / "config.json"
        config_path = i if i.exists() else c if c.exists() else None

        if config_path:
            with open(config_path, "r") as file:
                conf = json.load(file)
            if "_class_name" in conf:
                class_name = conf["_class_name"]
            elif "architectures" in conf:
                class_name = conf["architectures"][0]
            else:
                class_name = None
        else:
            error_hint = f"No model_index.json or config.json found in {folder_path}."

        if class_name and (type := cls.CLASS2TYPE.get(class_name)):
            return type
        else:
            error_hint = f"class {class_name} is not one of the supported classes [{', '.join(cls.CLASS2TYPE.keys())}]"

        # give up
        raise InvalidModelConfigException(
            f"Unable to determine model type for {folder_path}" + (f"; {error_hint}" if error_hint else "")
        )

    @classmethod
    def _get_checkpoint_config_path(
        cls,
        model_path: Path,
        model_type: ModelType,
        base_type: BaseModelType,
        variant_type: ModelVariantType,
        prediction_type: SchedulerPredictionType,
    ) -> Path:
        # look for a YAML file adjacent to the model file first
        possible_conf = model_path.with_suffix(".yaml")
        if possible_conf.exists():
            return possible_conf.absolute()

        if model_type is ModelType.Main:
            config_file = LEGACY_CONFIGS[base_type][variant_type]
            if isinstance(config_file, dict):  # need another tier for sd-2.x models
                config_file = config_file[prediction_type]
            config_file = f"stable-diffusion/{config_file}"
        elif model_type is ModelType.ControlNet:
            config_file = (
                "controlnet/cldm_v15.yaml"
                if base_type is BaseModelType.StableDiffusion1
                else "controlnet/cldm_v21.yaml"
            )
        elif model_type is ModelType.VAE:
            config_file = (
                "stable-diffusion/v1-inference.yaml"
                if base_type is BaseModelType.StableDiffusion1
                else "stable-diffusion/sd_xl_base.yaml"
                if base_type is BaseModelType.StableDiffusionXL
                else "stable-diffusion/v2-inference.yaml"
            )
        else:
            raise InvalidModelConfigException(
                f"{model_path}: Unrecognized combination of model_type={model_type}, base_type={base_type}"
            )
        return Path(config_file)

    @classmethod
    def _scan_and_load_checkpoint(cls, model_path: Path) -> CkptType:
        with SilenceWarnings():
            if model_path.suffix.endswith((".ckpt", ".pt", ".pth", ".bin")):
                cls._scan_model(model_path.name, model_path)
                model = torch.load(model_path, map_location="cpu")
                assert isinstance(model, dict)
                return model
            else:
                return safetensors.torch.load_file(model_path)

    @classmethod
    def _scan_model(cls, model_name: str, checkpoint: Path) -> None:
        """
        Apply picklescanner to the indicated checkpoint and issue a warning
        and option to exit if an infected file is identified.
        """
        # scan model
        scan_result = scan_file_path(checkpoint)
        if scan_result.infected_files != 0:
            raise Exception("The model {model_name} is potentially infected by malware. Aborting import.")


# Probing utilities
MODEL_NAME_TO_PREPROCESSOR = {
    "canny": "canny_image_processor",
    "mlsd": "mlsd_image_processor",
    "depth": "depth_anything_image_processor",
    "bae": "normalbae_image_processor",
    "normal": "normalbae_image_processor",
    "sketch": "pidi_image_processor",
    "scribble": "lineart_image_processor",
    "lineart": "lineart_image_processor",
    "lineart_anime": "lineart_anime_image_processor",
    "softedge": "hed_image_processor",
    "shuffle": "content_shuffle_image_processor",
    "pose": "dw_openpose_image_processor",
    "mediapipe": "mediapipe_face_processor",
    "pidi": "pidi_image_processor",
    "zoe": "zoe_depth_image_processor",
    "color": "color_map_image_processor",
}


def get_default_settings_controlnet_t2i_adapter(model_name: str) -> Optional[ControlAdapterDefaultSettings]:
    for k, v in MODEL_NAME_TO_PREPROCESSOR.items():
        if k in model_name:
            return ControlAdapterDefaultSettings(preprocessor=v)
    return None


def get_default_settings_main(model_base: BaseModelType) -> Optional[MainModelDefaultSettings]:
    if model_base is BaseModelType.StableDiffusion1 or model_base is BaseModelType.StableDiffusion2:
        return MainModelDefaultSettings(width=512, height=512)
    elif model_base is BaseModelType.StableDiffusionXL:
        return MainModelDefaultSettings(width=1024, height=1024)
    # We don't provide defaults for BaseModelType.StableDiffusionXLRefiner, as they are not standalone models.
    return None


# ##################################################3
# Checkpoint probing
# ##################################################3


class CheckpointProbeBase(ProbeBase):
    def __init__(self, model_path: Path):
        super().__init__(model_path)
        self.checkpoint = ModelProbe._scan_and_load_checkpoint(model_path)

    def get_format(self) -> ModelFormat:
        return ModelFormat("checkpoint")

    def get_variant_type(self) -> ModelVariantType:
        model_type = ModelProbe.get_model_type_from_checkpoint(self.model_path, self.checkpoint)
        if model_type != ModelType.Main:
            return ModelVariantType.Normal
        state_dict = self.checkpoint.get("state_dict") or self.checkpoint
        in_channels = state_dict["model.diffusion_model.input_blocks.0.0.weight"].shape[1]
        if in_channels == 9:
            return ModelVariantType.Inpaint
        elif in_channels == 5:
            return ModelVariantType.Depth
        elif in_channels == 4:
            return ModelVariantType.Normal
        else:
            raise InvalidModelConfigException(
                f"Cannot determine variant type (in_channels={in_channels}) at {self.model_path}"
            )


class PipelineCheckpointProbe(CheckpointProbeBase):
    def get_base_type(self) -> BaseModelType:
        checkpoint = self.checkpoint
        state_dict = self.checkpoint.get("state_dict") or checkpoint
        key_name = "model.diffusion_model.input_blocks.2.1.transformer_blocks.0.attn2.to_k.weight"
        if key_name in state_dict and state_dict[key_name].shape[-1] == 768:
            return BaseModelType.StableDiffusion1
        if key_name in state_dict and state_dict[key_name].shape[-1] == 1024:
            return BaseModelType.StableDiffusion2
        key_name = "model.diffusion_model.input_blocks.4.1.transformer_blocks.0.attn2.to_k.weight"
        if key_name in state_dict and state_dict[key_name].shape[-1] == 2048:
            return BaseModelType.StableDiffusionXL
        elif key_name in state_dict and state_dict[key_name].shape[-1] == 1280:
            return BaseModelType.StableDiffusionXLRefiner
        else:
            raise InvalidModelConfigException("Cannot determine base type")

    def get_scheduler_prediction_type(self) -> SchedulerPredictionType:
        """Return model prediction type."""
        type = self.get_base_type()
        if type == BaseModelType.StableDiffusion2:
            checkpoint = self.checkpoint
            state_dict = self.checkpoint.get("state_dict") or checkpoint
            key_name = "model.diffusion_model.input_blocks.2.1.transformer_blocks.0.attn2.to_k.weight"
            if key_name in state_dict and state_dict[key_name].shape[-1] == 1024:
                if "global_step" in checkpoint:
                    if checkpoint["global_step"] == 220000:
                        return SchedulerPredictionType.Epsilon
                    elif checkpoint["global_step"] == 110000:
                        return SchedulerPredictionType.VPrediction
            return SchedulerPredictionType.VPrediction  # a guess for sd2 ckpts

        elif type == BaseModelType.StableDiffusion1:
            return SchedulerPredictionType.Epsilon  # a reasonable guess for sd1 ckpts
        else:
            return SchedulerPredictionType.Epsilon


class VaeCheckpointProbe(CheckpointProbeBase):
    def get_base_type(self) -> BaseModelType:
        # VAEs of all base types have the same structure, so we wimp out and
        # guess using the name.
        for regexp, basetype in [
            (r"xl", BaseModelType.StableDiffusionXL),
            (r"sd2", BaseModelType.StableDiffusion2),
            (r"vae", BaseModelType.StableDiffusion1),
        ]:
            if re.search(regexp, self.model_path.name, re.IGNORECASE):
                return basetype
        raise InvalidModelConfigException("Cannot determine base type")


class LoRACheckpointProbe(CheckpointProbeBase):
    """Class for LoRA checkpoints."""

    def get_format(self) -> ModelFormat:
        return ModelFormat("lycoris")

    def get_base_type(self) -> BaseModelType:
        checkpoint = self.checkpoint
        token_vector_length = lora_token_vector_length(checkpoint)

        if token_vector_length == 768:
            return BaseModelType.StableDiffusion1
        elif token_vector_length == 1024:
            return BaseModelType.StableDiffusion2
        elif token_vector_length == 1280:
            return BaseModelType.StableDiffusionXL  # recognizes format at https://civitai.com/models/224641
        elif token_vector_length == 2048:
            return BaseModelType.StableDiffusionXL
        else:
            raise InvalidModelConfigException(f"Unknown LoRA type: {self.model_path}")


class TextualInversionCheckpointProbe(CheckpointProbeBase):
    """Class for probing embeddings."""

    def get_format(self) -> ModelFormat:
        return ModelFormat.EmbeddingFile

    def get_base_type(self) -> BaseModelType:
        checkpoint = self.checkpoint
        if "string_to_token" in checkpoint:
            token_dim = list(checkpoint["string_to_param"].values())[0].shape[-1]
        elif "emb_params" in checkpoint:
            token_dim = checkpoint["emb_params"].shape[-1]
        elif "clip_g" in checkpoint:
            token_dim = checkpoint["clip_g"].shape[-1]
        else:
            token_dim = list(checkpoint.values())[0].shape[0]
        if token_dim == 768:
            return BaseModelType.StableDiffusion1
        elif token_dim == 1024:
            return BaseModelType.StableDiffusion2
        elif token_dim == 1280:
            return BaseModelType.StableDiffusionXL
        else:
            raise InvalidModelConfigException(f"{self.model_path}: Could not determine base type")


class ControlNetCheckpointProbe(CheckpointProbeBase):
    """Class for probing controlnets."""

    def get_base_type(self) -> BaseModelType:
        checkpoint = self.checkpoint
        for key_name in (
            "control_model.input_blocks.2.1.transformer_blocks.0.attn2.to_k.weight",
            "controlnet_mid_block.bias",
            "input_blocks.2.1.transformer_blocks.0.attn2.to_k.weight",
            "down_blocks.1.attentions.0.transformer_blocks.0.attn2.to_k.weight",
        ):
            if key_name not in checkpoint:
                continue
            width = checkpoint[key_name].shape[-1]
            if width == 768:
                return BaseModelType.StableDiffusion1
            elif width == 1024:
                return BaseModelType.StableDiffusion2
            elif width == 2048:
                return BaseModelType.StableDiffusionXL
            elif width == 1280:
                return BaseModelType.StableDiffusionXL
        raise InvalidModelConfigException(f"{self.model_path}: Unable to determine base type")


class IPAdapterCheckpointProbe(CheckpointProbeBase):
    """Class for probing IP Adapters"""

    def get_base_type(self) -> BaseModelType:
        checkpoint = self.checkpoint
        for key in checkpoint.keys():
            if not key.startswith(("image_proj.", "ip_adapter.")):
                continue
            cross_attention_dim = checkpoint["ip_adapter.1.to_k_ip.weight"].shape[-1]
            if cross_attention_dim == 768:
                return BaseModelType.StableDiffusion1
            elif cross_attention_dim == 1024:
                return BaseModelType.StableDiffusion2
            elif cross_attention_dim == 2048:
                return BaseModelType.StableDiffusionXL
            else:
                raise InvalidModelConfigException(
                    f"IP-Adapter had unexpected cross-attention dimension: {cross_attention_dim}."
                )
        raise InvalidModelConfigException(f"{self.model_path}: Unable to determine base type")


class CLIPVisionCheckpointProbe(CheckpointProbeBase):
    def get_base_type(self) -> BaseModelType:
        raise NotImplementedError()


class T2IAdapterCheckpointProbe(CheckpointProbeBase):
    def get_base_type(self) -> BaseModelType:
        raise NotImplementedError()


class SpandrelImageToImageCheckpointProbe(CheckpointProbeBase):
    def get_base_type(self) -> BaseModelType:
        return BaseModelType.Any


########################################################
# classes for probing folders
#######################################################
class FolderProbeBase(ProbeBase):
    def get_variant_type(self) -> ModelVariantType:
        return ModelVariantType.Normal

    def get_format(self) -> ModelFormat:
        return ModelFormat("diffusers")

    def get_repo_variant(self) -> ModelRepoVariant:
        # get all files ending in .bin or .safetensors
        weight_files = list(self.model_path.glob("**/*.safetensors"))
        weight_files.extend(list(self.model_path.glob("**/*.bin")))
        for x in weight_files:
            if ".fp16" in x.suffixes:
                return ModelRepoVariant.FP16
            if "openvino_model" in x.name:
                return ModelRepoVariant.OpenVINO
            if "flax_model" in x.name:
                return ModelRepoVariant.Flax
            if x.suffix == ".onnx":
                return ModelRepoVariant.ONNX
        return ModelRepoVariant.Default


class PipelineFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        with open(self.model_path / "unet" / "config.json", "r") as file:
            unet_conf = json.load(file)
        if unet_conf["cross_attention_dim"] == 768:
            return BaseModelType.StableDiffusion1
        elif unet_conf["cross_attention_dim"] == 1024:
            return BaseModelType.StableDiffusion2
        elif unet_conf["cross_attention_dim"] == 1280:
            return BaseModelType.StableDiffusionXLRefiner
        elif unet_conf["cross_attention_dim"] == 2048:
            return BaseModelType.StableDiffusionXL
        else:
            raise InvalidModelConfigException(f"Unknown base model for {self.model_path}")

    def get_scheduler_prediction_type(self) -> SchedulerPredictionType:
        with open(self.model_path / "scheduler" / "scheduler_config.json", "r") as file:
            scheduler_conf = json.load(file)
        if scheduler_conf.get("prediction_type", "epsilon") == "v_prediction":
            return SchedulerPredictionType.VPrediction
        elif scheduler_conf.get("prediction_type", "epsilon") == "epsilon":
            return SchedulerPredictionType.Epsilon
        else:
            raise InvalidModelConfigException("Unknown scheduler prediction type: {scheduler_conf['prediction_type']}")

    def get_variant_type(self) -> ModelVariantType:
        # This only works for pipelines! Any kind of
        # exception results in our returning the
        # "normal" variant type
        try:
            config_file = self.model_path / "unet" / "config.json"
            with open(config_file, "r") as file:
                conf = json.load(file)

            in_channels = conf["in_channels"]
            if in_channels == 9:
                return ModelVariantType.Inpaint
            elif in_channels == 5:
                return ModelVariantType.Depth
            elif in_channels == 4:
                return ModelVariantType.Normal
        except Exception:
            pass
        return ModelVariantType.Normal


class VaeFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        if self._config_looks_like_sdxl():
            return BaseModelType.StableDiffusionXL
        elif self._name_looks_like_sdxl():
            # but SD and SDXL VAE are the same shape (3-channel RGB to 4-channel float scaled down
            # by a factor of 8), we can't necessarily tell them apart by config hyperparameters.
            return BaseModelType.StableDiffusionXL
        else:
            return BaseModelType.StableDiffusion1

    def _config_looks_like_sdxl(self) -> bool:
        # config values that distinguish Stability's SD 1.x VAE from their SDXL VAE.
        config_file = self.model_path / "config.json"
        if not config_file.exists():
            raise InvalidModelConfigException(f"Cannot determine base type for {self.model_path}")
        with open(config_file, "r") as file:
            config = json.load(file)
        return config.get("scaling_factor", 0) == 0.13025 and config.get("sample_size") in [512, 1024]

    def _name_looks_like_sdxl(self) -> bool:
        return bool(re.search(r"xl\b", self._guess_name(), re.IGNORECASE))

    def _guess_name(self) -> str:
        name = self.model_path.name
        if name == "vae":
            name = self.model_path.parent.name
        return name


class TextualInversionFolderProbe(FolderProbeBase):
    def get_format(self) -> ModelFormat:
        return ModelFormat.EmbeddingFolder

    def get_base_type(self) -> BaseModelType:
        path = self.model_path / "learned_embeds.bin"
        if not path.exists():
            raise InvalidModelConfigException(
                f"{self.model_path.as_posix()} does not contain expected 'learned_embeds.bin' file"
            )
        return TextualInversionCheckpointProbe(path).get_base_type()


class ONNXFolderProbe(PipelineFolderProbe):
    def get_base_type(self) -> BaseModelType:
        # Due to the way the installer is set up, the configuration file for safetensors
        # will come along for the ride if both the onnx and safetensors forms
        # share the same directory. We take advantage of this here.
        if (self.model_path / "unet" / "config.json").exists():
            return super().get_base_type()
        else:
            logger.warning('Base type probing is not implemented for ONNX models. Assuming "sd-1"')
            return BaseModelType.StableDiffusion1

    def get_format(self) -> ModelFormat:
        return ModelFormat("onnx")

    def get_variant_type(self) -> ModelVariantType:
        return ModelVariantType.Normal


class ControlNetFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        config_file = self.model_path / "config.json"
        if not config_file.exists():
            raise InvalidModelConfigException(f"Cannot determine base type for {self.model_path}")
        with open(config_file, "r") as file:
            config = json.load(file)
        # no obvious way to distinguish between sd2-base and sd2-768
        dimension = config["cross_attention_dim"]
        base_model = (
            BaseModelType.StableDiffusion1
            if dimension == 768
            else (
                BaseModelType.StableDiffusion2
                if dimension == 1024
                else BaseModelType.StableDiffusionXL
                if dimension == 2048
                else None
            )
        )
        if not base_model:
            raise InvalidModelConfigException(f"Unable to determine model base for {self.model_path}")
        return base_model


class LoRAFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        model_file = None
        for suffix in ["safetensors", "bin"]:
            base_file = self.model_path / f"pytorch_lora_weights.{suffix}"
            if base_file.exists():
                model_file = base_file
                break
        if not model_file:
            raise InvalidModelConfigException("Unknown LoRA format encountered")
        return LoRACheckpointProbe(model_file).get_base_type()


class IPAdapterFolderProbe(FolderProbeBase):
    def get_format(self) -> ModelFormat:
        return ModelFormat.InvokeAI

    def get_base_type(self) -> BaseModelType:
        model_file = self.model_path / "ip_adapter.bin"
        if not model_file.exists():
            raise InvalidModelConfigException("Unknown IP-Adapter model format.")

        state_dict = torch.load(model_file, map_location="cpu")
        cross_attention_dim = state_dict["ip_adapter"]["1.to_k_ip.weight"].shape[-1]
        if cross_attention_dim == 768:
            return BaseModelType.StableDiffusion1
        elif cross_attention_dim == 1024:
            return BaseModelType.StableDiffusion2
        elif cross_attention_dim == 2048:
            return BaseModelType.StableDiffusionXL
        else:
            raise InvalidModelConfigException(
                f"IP-Adapter had unexpected cross-attention dimension: {cross_attention_dim}."
            )

    def get_image_encoder_model_id(self) -> Optional[str]:
        encoder_id_path = self.model_path / "image_encoder.txt"
        if not encoder_id_path.exists():
            return None
        with open(encoder_id_path, "r") as f:
            image_encoder_model = f.readline().strip()
        return image_encoder_model


class CLIPVisionFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        return BaseModelType.Any


class SpandrelImageToImageFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        raise NotImplementedError()


class T2IAdapterFolderProbe(FolderProbeBase):
    def get_base_type(self) -> BaseModelType:
        config_file = self.model_path / "config.json"
        if not config_file.exists():
            raise InvalidModelConfigException(f"Cannot determine base type for {self.model_path}")
        with open(config_file, "r") as file:
            config = json.load(file)

        adapter_type = config.get("adapter_type", None)
        if adapter_type == "full_adapter_xl":
            return BaseModelType.StableDiffusionXL
        elif adapter_type == "full_adapter" or "light_adapter":
            # I haven't seen any T2I adapter models for SD2, so assume that this is an SD1 adapter.
            return BaseModelType.StableDiffusion1
        else:
            raise InvalidModelConfigException(
                f"Unable to determine base model for '{self.model_path}' (adapter_type = {adapter_type})."
            )


# Register probe classes
ModelProbe.register_probe("diffusers", ModelType.Main, PipelineFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.VAE, VaeFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.LoRA, LoRAFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.TextualInversion, TextualInversionFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.ControlNet, ControlNetFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.IPAdapter, IPAdapterFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.CLIPVision, CLIPVisionFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.T2IAdapter, T2IAdapterFolderProbe)
ModelProbe.register_probe("diffusers", ModelType.SpandrelImageToImage, SpandrelImageToImageFolderProbe)

ModelProbe.register_probe("checkpoint", ModelType.Main, PipelineCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.VAE, VaeCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.LoRA, LoRACheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.TextualInversion, TextualInversionCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.ControlNet, ControlNetCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.IPAdapter, IPAdapterCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.CLIPVision, CLIPVisionCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.T2IAdapter, T2IAdapterCheckpointProbe)
ModelProbe.register_probe("checkpoint", ModelType.SpandrelImageToImage, SpandrelImageToImageCheckpointProbe)

ModelProbe.register_probe("onnx", ModelType.ONNX, ONNXFolderProbe)
