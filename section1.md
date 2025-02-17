## 1. Why are low-resource languages challenging for natural language processing and large language models? Discuss this with reference to tokenisation.

Tokenisation is essential in NLP, as it determines how text is broken down into units that the model can understand. If tokenisation is not performed well, the model will misunderstand words, break important phrases, and get confused with mixed languages. In the following, I will explain how tokenisation can affect NLP model performance in low-resource languages, especially Singlish, in two aspects.

**a. Missing Words in Tokenizer**: Tokenizer does not recognize code-switching words in Singlish, leading to `[UNK]` (unknown token).

Singlish mixes English, Chinese, and Malay. Since most NLP models’ training data focuses on high-resource languages like English, but not low-resource languages like Singlish, this causes the model not to find the input Singlish vocabulary in the standard tokenizers during tokenisation. This will lead to out-of-vocabulary issues.

> eg: Input: “kopi siew dai one”,
>
> After tokenisation: “["[UNK]", "[UNK]", "[UNK]", "one"]

**b. Wrong Splitting**: Tokenizer splits words or phrases incorrectly, changing the meaning.

Some Singlish phrases consist of two or more words, which have different meanings from the individual English words. If the tokenizer splits them wrongly, the model will get confused.

> eg: Input: “It is a Die Die Must Have feature.”
>
> After tokenisation: ["It", "is", "a", "Die", "Die", "Must", "Have", "feature"].
>
> Good tokenisation example: ["It", "is", "a", "Die_Die_Must”, “have", "feature"]

Besides these challenges in the tokenisation part, there are also other challenges in NLP for low-resource languages. Even the same term can have different meanings in a low-resource language background. For example, "Last time" in Singlish also means a long time ago.

---
## 2. What implications does this paper have for the development of safety guardrails for LLMs in countries with low-resource languages?
**a. The importance of a safety risk taxonomy aligned to the local context.**

Some harmful content is universal (like extreme violence or child exploitation),  but meanwhile, some risky content can vary by region because of cultural and legal differences. This means generic safety guardrails (Moderation API, Perspective API and LlamaGuard) might not suit every region or language, especially for the low-resource languages.
    
**b. The paper designed a reusable methodology for all low-resource languages to build a localized data set and model.**

The authors generated a Singlish dataset, which is a valuable resource for similar studies.
The model also outperformed general APIs on Singlish texts.

---

## 3. Why was PR-AUC used as the evaluation metric for LionGuard over other performance metrics? In what situations would a F1-score be preferable?

As in chapter 4.4: “Due to the heavily imbalanced dataset, we chose the Precision-Recall AUC (PRAUC) as our evaluation metric as it can better represent the classifier’s ability to detect unsafe content across all score thresholds.”

Since the dataset is imbalanced, there are more safe texts than unsafe ones. Meanwhile, false negatives (FN) are much more serious than false positives (FP). If the model fails to catch unsafe content, it can cause real harm. F1-score does not distinguish between FN and FP, as it is the harmonic mean of precision and recall. If precision is high but recall is low (meaning the model is missing a lot of unsafe content), F1-score can still appear reasonable. For example, if the model predicts everything as safe, the F1-score can still be high, even though the model is actually failing to detect unsafe content, which makes F1-score misleading in this situation. 

Therefore, PR-AUC is a better evaluation metric in this case because it considers the model’s ability to distinguish unsafe content across different classification thresholds, rather than relying on a fixed decision boundary. Unlike F1-score, which balances precision and recall equally, PR-AUC provides a more comprehensive view by evaluating the trade-off between them across all possible thresholds. This makes it more suitable for imbalanced datasets where recall is critical, as it ensures that the model is evaluated on how well it can detect unsafe content without being overly influenced by the majority class (safe content). 

And F1-score will be a good option for general classification tasks when:

* data is balanced
* FP and FN need to be trade-off
  

---

## 4. What are some weaknesses in LionGuard’s methodology?

AI is growing rapidly and will affect many parts of everyone's daily life. Therefore, AI safety issues are very important and a safety risk taxonomy aligned to the local context is the first and highest priority to work on. This paper will be a strong foundation for AI development in Singlish and other low-resource languages. 

To further improve the quality of the paper, I would suggest the following aspects:

**(1) Robustness of the dataset**

**a. Balanced dataset** 
For balancing the data, the authors have considered obtaining data from various sources and periods. They have also unsampled the safe and unsafe data after finding that their distribution was imbalanced. Here, I propose some possible strategies to further enhance the dataset.
* When collecting the data, did a quick check on the diversity of the gender/nationality/age and more factors. The reason is that the source data heavily relies on the forum data, but the forum data may bring biases to the model. For example, people will wonder if the users in the selected forum are usually males aged 18-35 years old and from the same nationality. In this case, collecting more data from various data sources may add more diversity to the final dataset to enhance its robustness.
* The paper does not show the details of how the authors clean the collected source data. It is necessary to carefully do data cleaning, removing repeated contents and meaningless texts before performing the down-sampling operation.
* The paper introduced that there are seven categories of safety risks, but the distribution of these seven classes in the training data after the down-sampling operation is also missing. If these seven categories of data are also distributed in an imbalanced way, further adjustment is needed. If the size of some specific categories is small, you can consider doing some data augmentation.

**b. Data augmentation**
Usage of generative adversarial datasets. Since more and more safety-detection modules are used by different websites/forums, it is foreseen that some users may try different methods to escape from the safeguard. For example, they can use combinations of safe words with similar pronunciation to represent unsafe words or split the unsafe words by various symbols to escape the token detection, e.g., $u!c1d3. To avoid this, you can generate some adversarial datasets using LLM APIs to further enhance the dataset. 

**c. Data quality**
The authors already collaborated with a company for human labelling of the data, and they also mentioned that the consistency of the justify among the labelling workers was not high in several risk categories. In this case, collaborating with laboratories in local universities may be helpful. The experts in language/law may further enhance the data quality, which is possible to make the dataset a ‘gold standard’ in the field.

**(2) Robustness of the model**
Besides the data down-sampling strategy that the authors adopted, there are some other recommended methods that can be tried. For example, you can try active learning which can learn more from “more difficult predictions” or “fewer samples”. Loss functions such as Focal Loss were another option, which can give higher weights to samples with few numbers or with more difficult class predictions.

**(3) Storyline of the paper**
In chapter 4.3.1, the authors introduced detailed experiments to show the results of prompt engineering for LLM labelling. I think this is cool, I also have done similar works in TikTok when labelling POI data using LLM APIs via prompt engineering. However, as the beginning of the results part, I personally think that this ablation study is too long since it is not the “selling point” of the paper. I would suggest that the authors should highlight more on the design and cleaning of the datasets as well as the designation of the model.
