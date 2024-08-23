from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, Union

import torch
from diffusers import UNet2DConditionModel
from diffusers.schedulers.scheduling_utils import SchedulerMixin, SchedulerOutput

if TYPE_CHECKING:
    from invokeai.backend.stable_diffusion.diffusion.conditioning_data import ConditioningMode, TextConditioningData


@dataclass
class UNetKwargs:
    sample: torch.Tensor
    timestep: Union[torch.Tensor, float, int]
    encoder_hidden_states: torch.Tensor

    class_labels: Optional[torch.Tensor] = None
    timestep_cond: Optional[torch.Tensor] = None
    attention_mask: Optional[torch.Tensor] = None
    cross_attention_kwargs: Optional[Dict[str, Any]] = None
    added_cond_kwargs: Optional[Dict[str, torch.Tensor]] = None
    down_block_additional_residuals: Optional[Tuple[torch.Tensor]] = None
    mid_block_additional_residual: Optional[torch.Tensor] = None
    down_intrablock_additional_residuals: Optional[Tuple[torch.Tensor]] = None
    encoder_attention_mask: Optional[torch.Tensor] = None
    # return_dict: bool = True


@dataclass
class DenoiseInputs:
    """Initial variables passed to denoise. Supposed to be unchanged."""

    # The latent-space image to denoise.
    # Shape: [batch, channels, latent_height, latent_width]
    # - If we are inpainting, this is the initial latent image before noise has been added.
    # - If we are generating a new image, this should be initialized to zeros.
    # - In some cases, this may be a partially-noised latent image (e.g. when running the SDXL refiner).
    orig_latents: torch.Tensor

    # kwargs forwarded to the scheduler.step() method.
    scheduler_step_kwargs: dict[str, Any]

    # Text conditionging data.
    conditioning_data: TextConditioningData

    # Noise used for two purposes:
    # 1. Used by the scheduler to noise the initial `latents` before denoising.
    # 2. Used to noise the `masked_latents` when inpainting.
    # `noise` should be None if the `latents` tensor has already been noised.
    # Shape: [1 or batch, channels, latent_height, latent_width]
    noise: Optional[torch.Tensor]

    # The seed used to generate the noise for the denoising process.
    # HACK(ryand): seed is only used in a particular case when `noise` is None, but we need to re-generate the
    # same noise used earlier in the pipeline. This should really be handled in a clearer way.
    seed: int

    # The timestep schedule for the denoising process.
    timesteps: torch.Tensor

    # The first timestep in the schedule. This is used to determine the initial noise level, so
    # should be populated if you want noise applied *even* if timesteps is empty.
    init_timestep: torch.Tensor

    # Class of attention processor that is used.
    attention_processor_cls: Type[Any]


@dataclass
class DenoiseContext:
    """Context with all variables in denoise"""

    # Initial variables passed to denoise. Supposed to be unchanged.
    inputs: DenoiseInputs

    # Scheduler which used to apply noise predictions.
    scheduler: SchedulerMixin

    # UNet model.
    unet: Optional[UNet2DConditionModel] = None

    # Current state of latent-space image in denoising process.
    # None until `PRE_DENOISE_LOOP` callback.
    # Shape: [batch, channels, latent_height, latent_width]
    latents: Optional[torch.Tensor] = None

    # Current denoising step index.
    # None until `PRE_STEP` callback.
    step_index: Optional[int] = None

    # Current denoising step timestep.
    # None until `PRE_STEP` callback.
    timestep: Optional[torch.Tensor] = None

    # Arguments which will be passed to UNet model.
    # Available in `PRE_UNET`/`POST_UNET` callbacks, otherwise will be None.
    unet_kwargs: Optional[UNetKwargs] = None

    # SchedulerOutput class returned from step function(normally, generated by scheduler).
    # Supposed to be used only in `POST_STEP` callback, otherwise can be None.
    step_output: Optional[SchedulerOutput] = None

    # Scaled version of `latents`, which will be passed to unet_kwargs initialization.
    # Available in events inside step(between `PRE_STEP` and `POST_STEP`).
    # Shape: [batch, channels, latent_height, latent_width]
    latent_model_input: Optional[torch.Tensor] = None

    # [TMP] Defines on which conditionings current unet call will be runned.
    # Available in `PRE_UNET`/`POST_UNET` callbacks, otherwise will be None.
    conditioning_mode: Optional[ConditioningMode] = None

    # [TMP] Noise predictions from negative conditioning.
    # Available in `POST_COMBINE_NOISE_PREDS` callback, otherwise will be None.
    # Shape: [batch, channels, latent_height, latent_width]
    negative_noise_pred: Optional[torch.Tensor] = None

    # [TMP] Noise predictions from positive conditioning.
    # Available in `POST_COMBINE_NOISE_PREDS` callback, otherwise will be None.
    # Shape: [batch, channels, latent_height, latent_width]
    positive_noise_pred: Optional[torch.Tensor] = None

    # Combined noise prediction from passed conditionings.
    # Available in `POST_COMBINE_NOISE_PREDS` callback, otherwise will be None.
    # Shape: [batch, channels, latent_height, latent_width]
    noise_pred: Optional[torch.Tensor] = None

    # Dictionary for extensions to pass extra info about denoise process to other extensions.
    extra: dict = field(default_factory=dict)
