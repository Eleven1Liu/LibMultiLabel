import torch.nn as nn
from transformers import AutoModelForSequenceClassification


class BERT(nn.Module):
    """BERT.

    Args:
        num_classes (int): Total number of classes.
        encoder_hidden_dropout (float): The dropout rate of the feed forward sublayer in each BERT layer. Defaults to 0.1.
        encoder_attention_dropout (float): The dropout rate of the attention sublayer in each BERT layer. Defaults to 0.1.
        post_encoder_dropout (float): The dropout rate of the dropout layer after the BERT model. Defaults to 0.
        lm_weight (str): Pretrained model name or path. Defaults to 'bert-base-cased'.
        lm_window (int): Length of the subsequences to be split before feeding them to
            the language model. Defaults to 512.
    """

    def __init__(
        self,
        num_classes,
        encoder_hidden_dropout=0.1,
        encoder_attention_dropout=0.1,
        post_encoder_dropout=0,
        lm_weight="bert-base-cased",
        lm_window=512,
        **kwargs,
    ):
        super().__init__()
        self.lm_window = lm_window

        self.lm = AutoModelForSequenceClassification.from_pretrained(
            lm_weight,
            num_labels=num_classes,
            hidden_dropout_prob=encoder_hidden_dropout,
            attention_probs_dropout_prob=encoder_attention_dropout,
            classifier_dropout=post_encoder_dropout,
            torchscript=True,
        )

    def forward(self, input):
        input_ids = input["text"]  # (batch_size, sequence_length)
        if input_ids.size(-1) > self.lm.config.max_position_embeddings:
            # Support for sequence length greater than 512 is not available yet
            raise ValueError(
                f"Got maximum sequence length {input_ids.size(-1)}, "
                f"please set max_seq_length to a value less than or equal to "
                f"{self.lm.config.max_position_embeddings}"
            )
        x = self.lm(input_ids, attention_mask=input_ids != self.lm.config.pad_token_id)[0]  # (batch_size, num_classes)
        return {"logits": x}
