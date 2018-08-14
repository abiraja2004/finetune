import os

import tensorflow as tf
from tensorflow.python.client import device_lib
from functools import lru_cache
from collections import namedtuple

# CONSTANTS
PAD_TOKEN = '<PAD>'


@lru_cache()
def all_gpus():
    """
    Get integer ids of all available GPUs
    """
    local_device_protos = device_lib.list_local_devices()
    return [
        int(x.name.split(':')[-1]) for x in local_device_protos
        if x.device_type == 'GPU'
    ]

GridSearchable = namedtuple("GridSearchable", "default iterator")


class Settings(dict):
    """
    Model configuration options

    :param batch_size: Number of examples per batch, defaults to `2`.
    :param visible_gpus: List of integer GPU ids to spread out computation across, defaults to all available GPUs.
    :param n_epochs: Number of iterations through training data, defaults to `3`.
    :param random_seed: Random seed to use for repeatability purposes, defaults to `42`.
    :param max_length:  Maximum number of subtokens per sequence. Examples longer than this number will be truncated 
        (unless `chunk_long_sequences=True` for SequenceLabeler models). Defaults to `512`.
    :param weight_stddev: Standard deviation of initial weights.  Defaults to `0.02`.
    :param chunk_long_sequences: When True, use a sliding window approach to predict on 
        examples that are longer than max length.  Defaults to `False`.
    :param low_memory_mode: When True, only store partial gradients on forward pass
        and recompute remaining gradients incrementally in order to save memory.  Defaults to `False`.
    :param interpolate_pos_embed: Interpolate positional embeddings when `max_length` differs from it's original value of 
        `512`. Defaults to `False`.
    :param embed_p_drop: Embedding dropout probability.  Defaults to `0.1`.
    :param attn_p_drop: Attention dropout probability.  Defaults to `0.1`.
    :param resid_p_drop: Residual layer fully connected network dropout probability.  Defaults to `0.1`.
    :param clf_p_drop: Classifier dropout probability.  Defaults to `0.1`.
    :param l2_reg: L2 regularization coefficient. Defaults to `0.01`.
    :param regularize_deviation: L2 penalty against pre-trained model weights.  Defaults to `0.0`.
    :param b1: Adam b1 parameter.  Defaults to `0.9`.
    :param b2: Adam b2 parameter.  Defaults to `0.999`.
    :param epsilon: Adam epsilon parameter: Defaults to `1e-8`.
    :param lr_schedule: Learning rate schedule -- see `finetune/optimizers.py` for more options.
    :param lr: Learning rate.  Defaults to `6.25e-5`.
    :param lr_warmup: Learning rate warmup (percentage of all batches to warmup for).  Defaults to `0.002`.
    :param max_grad_norm: Clip gradients larger than this norm. Defaults to `1.0`.
    :param lm_loss_coef: Language modeling loss coefficient -- a value between `0.0` - `1.0`
        that indicates how to trade off between language modeling loss
        and target model loss.  Usually not beneficial to turn on unless 
        dataset size exceeds a few thousand examples.  Defaults to `0.0`.
    :param summarize_grads: Include gradient summary information in tensorboard.  Defaults to `False`.
    :param verbose: Print TQDM logs?  Defaults to `True`.
    :param val_size: Validation set size as a percentage of all training data.  Defaults to `0.05`. 
    :param val_interval: Evaluate on validation set after `val_interval` batches.  Defaults to `150`.
    :param val_window_size: Print running average of validation score over `val_window_size` batches.  Defaults to `5`.
    :param rolling_avg_decay: Momentum-style parameter to smooth out validation estimates printed during training. Defaults to `0.99`.
    :param lm_temp: Language model temperature -- a value of `0.0` corresponds to greedy maximum likelihood predictions 
        while a value of `1.0` corresponds to random predictions. Defaults to `0.2`. 
    :param seq_num_heads: Number of attention heads of final attention layer. Defaults to `16`.
    :param subtoken_predictions: Return predictions at subtoken granularity or token granularity?  Defaults to `False`.
    :param multi_label_threshold: Threshold of sigmoid unit in multi label classifier. 
        Can be increased or lowered to trade off precision / recall. Defaults to `0.5`.
    :param autosave_path: Save current best model (as measured by validation loss) to this location. Defaults to `None`.
    :param tensorboard_folder: Directory for tensorboard logs. Tensorboard logs will not be written 
        unless tensorboard_folder is explicitly provided. Defaults to `None`.
    :param log_device_placement: Log which device each operation is placed on for debugging purposes.  Defaults to `False`.
    :param allow_soft_placement: Allow tf to allocate an operation to a different device if a device is unavailable.  Defaults to `True`.
    :param save_adam_vars: Save adam parameters when calling `model.save()`.  Defaults to `True`.
    :param num_layers_trained: How many layers to finetune.  Specifying a value less than 12 will train layers starting from model output. Defaults to `12`.
    :param train_embeddings: Should embedding layer be finetuned? Defaults to `True`.
    """
    def get_grid_searchable(self):
        return self.grid_searchable

    def __init__(self, **kwargs):
        super().__init__()
        self.grid_searchable = {}
        for key, value in kwargs.items():
            self[key] = value

    def __getattr__(self, attr):
        if attr.startswith('__'):
            raise AttributeError
        return self[attr]

    def __setitem__(self, key, value):
        if isinstance(value, GridSearchable):
            self.grid_searchable[key] = value.iterator
            value = value.default
        return super().__setitem__(key, value)

    def __setattr__(self, k, v):
        return self.__setitem__(k, v)

    __delattr__ = dict.__delitem__


def get_default_config():
    """
    Gets a config object containing all the default parameters for each variant of the model.

    :return: Config object.
    """
    return Settings(
        batch_size=2,
        visible_gpus=all_gpus(),
        n_epochs=GridSearchable(3, [1, 2, 3, 4]),
        seed=42,
        max_length=512,
        weight_stddev=0.02,
        chunk_long_sequences=False,
        low_memory_mode=False,
        interpolate_pos_embed=True,
        embed_p_drop=0.1,
        attn_p_drop=0.1,
        resid_p_drop=0.1,
        clf_p_drop=0.1,
        l2_reg=GridSearchable(0.01, [0.0, 0.1, 0.01, 0.001]),
        vector_l2=False,
        regularize_deviation=False,
        b1=0.9, 
        b2=0.999,
        epsilon=1e-8,
        lr_schedule='warmup_linear',
        lr=GridSearchable(6.25e-5, [6.25e-4, 6.25e-5, 6.25e-6]),
        lr_warmup=0.002,
        max_grad_norm=1,
        lm_loss_coef=0.0,
        summarize_grads=False,
        verbose=True,
        val_size=0.05,
        val_interval=150,
        val_window_size=5,
        rolling_avg_decay=0.99,
        lm_temp=0.2,
        seq_num_heads=16,
        pad_token="<PAD>",
        subtoken_predictions=False,
        multi_label_threshold=0.5,
        autosave_path=None,
        tensorboard_folder=None,
        log_device_placement=False,
        soft_device_placement=True,
        save_adam_vars=False,
        num_layers_trained=12,
        train_embeddings=True,
        class_weights=None

        # Must remain fixed
        n_heads=12,
        n_layer=12,
        act_fn="gelu",
        n_embed=768,
        base_model_path=os.path.join(os.path.dirname(__file__), "model", "Base_model.jl")
    )


def get_small_model_config():
    conf = get_default_config()
    conf.n_heads = 8
    conf.n_embed = 512
    conf.n_layer = 6
    conf.num_layers_trained=6
    conf.base_model_path = os.path.join(os.path.dirname(__file__), "model", "SmallBaseModel.jl")
    return conf


def get_config(**kwargs):
    """
    Gets a config object containing all the default parameters for each variant of the model.

    :param **kwargs: Keyword arguments to override default values.
    :return: Config object.    """
    config = get_default_config()
    config.update(kwargs)
    return config


def cpu_config():
    config = get_default_config()
    config.visible_gpus = []
    return config
