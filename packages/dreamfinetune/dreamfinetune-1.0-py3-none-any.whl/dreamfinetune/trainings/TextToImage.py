import itertools
import math
import os

import bitsandbytes as bnb
import torch
import torch.nn.functional as F
import torch.utils.checkpoint
from accelerate import Accelerator
from accelerate.logging import get_logger
from accelerate.utils import set_seed
from diffusers import (AutoencoderKL, DDPMScheduler, StableDiffusionPipeline, UNet2DConditionModel)
from diffusers.optimization import get_scheduler
from huggingface_hub import upload_folder
from torch.utils.data import Dataset
from tqdm.auto import tqdm
from transformers import CLIPTextModel, CLIPTokenizer

from ..utils import DreamBoothTextToImageDataset


class StableDiffusionTextToImageFineTune:

    def __init__(self, pretrained_model_name_or_path, resolution, center_crop,
                 train_text_encoder, dataset, dataset_config_name,
                 dataset_column, instance_prompt, learning_rate,
                 max_training_steps, save_steps, train_batch_size,
                 gradient_accumulation_steps, max_grad_norm,
                 mixed_precision, gradient_checkpointing,
                 use_8bit_adam, seed, with_prior_preservation,
                 prior_loss_weight, sample_batch_size, class_data_dir,
                 class_prompt, num_class_images, lr_scheduler,
                 lr_warmup_steps, output_dir, push_to_hub,
                 repo_id, token, max_training_epochs, max_train_steps):
        """
        Ініціалізує об'єкт для fine-tuning моделі Stable Diffusion на завданні inpainting.

        Args:
            pretrained_model_name_or_path (str): Шлях або ім'я попередньо натренованої моделі.
            resolution (int): Роздільна здатність зображень, до якої будуть масштабуватися вхідні дані.
            center_crop (bool): Використовувати центральний crop під час підготовки даних.
            train_text_encoder (bool): Визначає, чи потрібно тренувати текстовий енкодер.
            dataset (str): Об'єкт датасету, який використовується для тренування.
            dataset_config_name (str): Назва конфігурації датасету, якщо є декілька варіантів.
            dataset_row_name (str): Назва рядка в датасеті, який використовується для тренування.
            instance_prompt (str): Текстовий prompt, що описує індивідуальні зображення.
            learning_rate (float): Початковий темп навчання.
            max_training_steps (int): Максимальна кількість кроків тренування.
            save_steps (int): Кількість кроків між збереженням контрольних точок.
            train_batch_size (int): Розмір батчу для тренування.
            gradient_accumulation_steps (int): Кількість кроків для акумуляції градієнтів перед оновленням параметрів.
            max_grad_norm (float): Максимальна норма градієнта для обрізки.
            mixed_precision (str): Використання змішаної точності ("fp16", "bf16" або None).
            gradient_checkpointing (bool): Використання збереження контрольних точок градієнта для зменшення використання пам'яті.
            use_8bit_adam (bool): Використання 8-бітного Adam оптимізатора для зменшення використання пам'яті.
            seed (int): Випадковий seed для повторюваності результатів.
            with_prior_preservation (bool): Використання збереження prior під час тренування для підтримки специфіки індивідуальних зображень.
            prior_loss_weight (float): Вага втрат prior у загальній функції втрат.
            sample_batch_size (int): Розмір батчу для генерації зразків під час тренування.
            class_data_dir (str): Директорія з класовими зображеннями для prior preservation.
            class_prompt (str): Текстовий prompt, що описує класові зображення.
            num_class_images (int): Кількість зображень для кожного класу.
            lr_scheduler (str): Планувальник темпу навчання ("linear", "cosine", тощо).
            lr_warmup_steps (int): Кількість кроків для прогріву темпу навчання.
            output_dir (str): Директорія для збереження результатів тренування.
            push_to_hub (bool): Чи завантажувати результати на Hugging Face Hub.
            repo_id (str): Ідентифікатор репозиторію на Hugging Face Hub.
            token (str): Токен для аутентифікації на Hugging Face Hub.
        """
        self.max_train_steps = max_train_steps
        self.pretrained_model_name_or_path = pretrained_model_name_or_path
        self.resolution = resolution
        self.center_crop = center_crop
        self.train_text_encoder = train_text_encoder
        self.dataset = dataset
        self.dataset_config_name = dataset_config_name
        self.dataset_column = dataset_column
        self.instance_prompt = instance_prompt
        self.learning_rate = learning_rate
        self.max_training_steps = max_training_steps
        self.save_steps = save_steps
        self.train_batch_size = train_batch_size
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.max_grad_norm = max_grad_norm
        self.mixed_precision = mixed_precision
        self.gradient_checkpointing = gradient_checkpointing
        self.use_8bit_adam = use_8bit_adam
        self.seed = seed
        self.with_prior_preservation = with_prior_preservation
        self.prior_loss_weight = prior_loss_weight
        self.sample_batch_size = sample_batch_size
        self.class_data_dir = class_data_dir
        self.class_prompt = class_prompt
        self.num_class_images = num_class_images
        self.lr_scheduler = lr_scheduler
        self.lr_warmup_steps = lr_warmup_steps
        self.output_dir = output_dir
        self.push_to_hub = push_to_hub
        self.repo_id = repo_id
        self.token = token
        self.max_training_epochs = max_training_epochs
        self.text_encoder, self.vae, self.unet, self.tokenizer = self.load_args_for_training()

    def load_args_for_training(self):
        text_encoder = CLIPTextModel.from_pretrained(
            self.pretrained_model_name_or_path, subfolder="text_encoder"
        )
        vae = AutoencoderKL.from_pretrained(
            self.pretrained_model_name_or_path, subfolder="vae"
        )
        unet = UNet2DConditionModel.from_pretrained(
            self.pretrained_model_name_or_path, subfolder="unet"
        )
        tokenizer = CLIPTokenizer.from_pretrained(
            self.pretrained_model_name_or_path,
            subfolder="tokenizer",
        )
        return text_encoder, vae, unet, tokenizer

    def __call__(self, text_encoder: CLIPTokenizer, vae: AutoencoderKL, unet: UNet2DConditionModel):
        logger = get_logger(__name__)
        set_seed(self.seed)

        accelerator = Accelerator(
            gradient_accumulation_steps=self.gradient_accumulation_steps,
            mixed_precision=self.mixed_precision,
        )

        if self.train_text_encoder and self.gradient_accumulation_steps > 1 and accelerator.num_processes > 1:
            raise ValueError(
                "Gradient accumulation is not supported when training the text encoder in distributed training."
            )

        vae.requires_grad_(False)
        if not self.train_text_encoder:
            text_encoder.requires_grad_(False)

        if self.gradient_checkpointing:
            unet.enable_gradient_checkpointing()
            if self.train_text_encoder:
                text_encoder.gradient_checkpointing_enable()

        optimizer_class = bnb.optim.AdamW8bit if self.use_8bit_adam else torch.optim.AdamW
        params_to_optimize = (
            itertools.chain(unet.parameters(),
                            text_encoder.parameters()) if self.train_text_encoder else unet.parameters()
        )
        optimizer = optimizer_class(params_to_optimize, lr=self.learning_rate)

        noise_scheduler = DDPMScheduler.from_config(self.pretrained_model_name_or_path, subfolder="scheduler")
        train_dataset = DreamBoothTextToImageDataset(self.dataset, self.dataset_config_name,
                                                     self.dataset_column, tokenizer=self.tokenizer)

        def collate_fn(examples):
            input_ids = [example["instance_prompt_ids"] for example in examples]
            pixel_values = [example["instance_images"] for example in examples]

            pixel_values = torch.stack(pixel_values).to(memory_format=torch.contiguous_format).float()
            input_ids = self.tokenizer.pad(
                {"input_ids": input_ids},
                padding="max_length",
                return_tensors="pt",
                max_length=self.tokenizer.model_max_length
            ).input_ids

            return {"input_ids": input_ids, "pixel_values": pixel_values}

        train_dataloader = torch.utils.data.DataLoader(
            train_dataset, batch_size=self.train_batch_size, shuffle=True, collate_fn=collate_fn, num_workers=4
        )

        lr_scheduler = get_scheduler(
            self.lr_scheduler, optimizer=optimizer,
            num_warmup_steps=self.lr_warmup_steps * self.gradient_accumulation_steps,
            num_training_steps=self.max_train_steps * self.gradient_accumulation_steps,
        )

        models_to_prepare = [unet, optimizer, train_dataloader, lr_scheduler]
        if self.train_text_encoder:
            models_to_prepare.insert(1, text_encoder)
        prepared_models = accelerator.prepare(*models_to_prepare)
        unet, optimizer, train_dataloader, lr_scheduler = prepared_models[:4]
        if self.train_text_encoder:
            text_encoder = prepared_models[1]

        weight_dtype = torch.float16 if accelerator.mixed_precision == "fp16" else (
            torch.bfloat16 if accelerator.mixed_precision == "bf16" else torch.float32
        )
        vae.to(accelerator.device, dtype=weight_dtype)
        vae.decoder.to("cuda")
        if not self.train_text_encoder:
            text_encoder.to(accelerator.device, dtype=weight_dtype)

        num_update_steps_per_epoch = math.ceil(len(train_dataloader) / self.gradient_accumulation_steps)
        num_train_epochs = math.ceil(self.max_train_steps / num_update_steps_per_epoch)

        total_batch_size = self.train_batch_size * accelerator.num_processes * self.gradient_accumulation_steps
        logger.info("***** Running training *****")
        logger.info(f"  Num examples = {len(train_dataset)}")
        logger.info(f"  Instantaneous batch size per device = {self.train_batch_size}")
        logger.info(f"  Total train batch size (w. parallel, distributed & accumulation) = {total_batch_size}")
        logger.info(f"  Gradient Accumulation steps = {self.gradient_accumulation_steps}")
        logger.info(f"  Total optimization steps = {self.max_train_steps}")

        progress_bar = tqdm(range(self.max_train_steps), disable=not accelerator.is_local_main_process)
        progress_bar.set_description("Steps")
        global_step = 0

        for epoch in range(num_train_epochs):
            unet.train()
            for step, batch in enumerate(train_dataloader):
                with accelerator.accumulate(unet):
                    latents = vae.encode(batch["pixel_values"].to(dtype=weight_dtype)).latent_dist.sample()
                    latents = latents * 0.18215

                    noise = torch.randn_like(latents)
                    bsz = latents.shape[0]
                    timesteps = torch.randint(0, noise_scheduler.config.num_train_timesteps, (bsz,),
                                              device=latents.device)
                    timesteps = timesteps.long()

                    noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)
                    encoder_hidden_states = text_encoder(batch["input_ids"])[0]
                    noise_pred = unet(noisy_latents, timesteps, encoder_hidden_states).sample

                    if noise_scheduler.config.prediction_type == "epsilon":
                        target = noise
                    elif noise_scheduler.config.prediction_type == "v_prediction":
                        target = noise_scheduler.get_velocity(latents, noise, timesteps)
                    else:
                        raise ValueError(f"Unknown prediction type {noise_scheduler.config.prediction_type}")

                    if self.with_prior_preservation:
                        noise_pred, noise_pred_prior = torch.chunk(noise_pred, 2, dim=0)
                        target, target_prior = torch.chunk(target, 2, dim=0)

                        loss = F.mse_loss(noise_pred.float(), target.float(), reduction="none").mean([1, 2, 3]).mean()
                        prior_loss = F.mse_loss(noise_pred_prior.float(), target_prior.float(), reduction="mean")
                        loss = loss + self.prior_loss_weight * prior_loss
                    else:
                        loss = F.mse_loss(noise_pred.float(), target.float(), reduction="mean")

                    accelerator.backward(loss)

                    if accelerator.sync_gradients:
                        accelerator.clip_grad_norm_(unet.parameters(), self.max_grad_norm)
                        optimizer.step()
                        optimizer.zero_grad(set_to_none=True)

                    if accelerator.sync_gradients:
                        progress_bar.update(1)
                        global_step += 1

                        if global_step % (self.save_steps * 2) == 0:
                            if accelerator.is_main_process:
                                pipeline = StableDiffusionPipeline.from_pretrained(
                                    self.pretrained_model_name_or_path,
                                    unet=accelerator.unwrap_model(unet),
                                    text_encoder=accelerator.unwrap_model(text_encoder),
                                )
                                save_path = os.path.join(self.output_dir, f"checkpoint-{global_step}")
                                pipeline.save_pretrained(save_path)

                    logs = {"loss": loss.detach().item()}
                    progress_bar.set_postfix(**logs)

                    if global_step >= self.max_train_steps:
                        break

            accelerator.wait_for_everyone()

        if accelerator.is_main_process:
            accelerator.init_trackers("dreambooth")
            pipeline = StableDiffusionPipeline.from_pretrained(
                self.pretrained_model_name_or_path,
                unet=accelerator.unwrap_model(unet),
                text_encoder=accelerator.unwrap_model(text_encoder),
            )
            pipeline.save_pretrained(self.output_dir)

            if self.push_to_hub:
                upload_folder(
                    repo_id=self.repo_id,
                    folder_path=self.output_dir,
                    commit_message="End of training",
                    ignore_patterns=["step_*", "epoch_*"],
                )

        accelerator.end_training()

