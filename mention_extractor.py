'''LABEL_INDEX = -1


def read_file(file_path):
    """
    Получает на вход путь к данным в CoNLL-формате. Выдает массив предложений, разбитых на слова
	:param file_path: путь к корпусу в CoNLL-формате
	:return: corpus_sentences - массив предложений, разбитых на слова
	"""

    corpus_sentences = []
    input_sentence = []
    with open(file_path, 'r', encoding='utf-8') as f_in:
        for line in f_in:
            line = line.strip()

            if len(line) == 0 or line[0] == '#':
                if len(input_sentence) > 0:
                    corpus_sentences.append(input_sentence)
                    input_sentence = []
                continue
            parts = line.split(' ')
            if len(parts) >= 2:
                input_sentence.append(parts)

    if len(input_sentence) > 0:
        corpus_sentences.append(input_sentence)

    print(file_path, len(corpus_sentences), "sentences")
    return corpus_sentences


def prepare_data(input_filepath, output_path, external_dev_path='', external_test_path=''):
    """
    Получает на вход путь к корпусу в CoNLL-формате.
    """
    corpus_sentences = read_file(input_filepath)

    char2idx, idx2char, n_char_types = count_char_types(corpus_sentences)

    label2idx, idx2label = get_label_types(corpus_sentences)

    with open(output_path + '.par', 'w', encoding='utf-8') as f_par:
        print(char2idx, file=f_par)
        print(idx2char, file=f_par)
        print(label2idx, file=f_par)
        print(idx2label, file=f_par)

    train_data = create_matrices(train_sentences, word2idx, char2idx, case2idx, label2idx)
    print(len(train_data), "train sentences")
    dev_data = create_matrices(dev_sentences, word2idx, char2idx, case2idx, label2idx)
    print(len(dev_data), "dev sentences")
    test_data = create_matrices(test_sentences, word2idx, char2idx, case2idx, label2idx)
    print(len(test_data), "test sentences")

    return train_data, dev_data, test_data, word_embeddings, case_embeddings, n_char_types, label2idx


def count_char_types(corpus_sentences):
    """
	Считаем по корпусу количество типов пунктуаторов и строим таблицу соответствия между пунктуатором и его индексом в
	словаре. Также учитываем 3 специальных символа - неизвестынй символ, символ паддинга предложания
	(считаем что паддинги состоят из специальных символов, которые нигде больше не встречаются)
	и END_OF_WORD - посмивольный паддинг слова до интересующей нас длины
	:param corpus_sentences: все предложения корпуса
	:return: char2idx, idx2char - соответствия симолов индексам и наоборот,а также общее количество типов символов
	"""
    charset = set()
    charset.add('END_OF_WORD')
    charset.add('other')
    charset.add('PADDING_TOKEN')

    for sentence in corpus_sentences:
        for token in sentence:
            token_text = token[0]
            charset.update(token_text)
    print(len(charset), sys.stderr)

    char2idx = {}
    idx2char = {}
    for char in charset:
        char2idx[char] = len(char2idx)
        idx2char[len(idx2char)] = char

    return char2idx, idx2char, len(char2idx)


def get_label_types(corpus_sentences):
    """
	Cтроим по корпусу таблицу соответствия между типами меток и их индексами в словаре
	:param corpus_sentences: все предложения корпуса
	:return: label2idx и idx2label прямой и обратный словари соответсвий меток и индексов
	"""
    label_set = set()
    label_set.add('Padding')
    for sentence in corpus_sentences:
        for token in sentence:
            if len(token) >= 2:
                if len(token[LABEL_INDEX]) == 0:
                    print('zero-length label: %s' % str(token))
                    continue
                label_set.add(token[LABEL_INDEX])
    label2idx = {}
    idx2label = {}

    for label in label_set:
        label2idx[label] = len(label2idx)
        idx2label[len(idx2label)] = label
    print(label2idx, sys.stderr)
    print(idx2label, sys.stderr)

    return label2idx, idx2label


def create_matrices(sentences, word2idx, char2idx, case2idx, label2idx):
    """
	По массиву предложений и словарям соответсвий признаков и индекосв получаем датасет в подходяшем для загрузки в
	нейросеть виде
	:param sentences: массив предложений
	:param word2idx: словарь соответсвия слов и индексов
	:param char2idx: словарь соответсвия символов и индексов
	:param case2idx: словарь соответсвия шаблонов капитализации и индексов
	:param label2idx: словарь соответсвия лейблов и индексов
	:return: dataset - данные в том виде, в котором их удобно загружать в нейросеть
	"""

    dataset = []
	total_tokens = 0
	unknown_tokens = 0
	for sentence in sentences:
		# добиваемся, чтобы длина предложения была всегда 2^(n+1) + 1, причем первый и последний символ обязаны быть
		# паддингами
		middle_token_idx = len(sentence) // 2
		window_size = get_window_size(len(sentence), middle_token_idx)
		# Индекс первого не паддинга в предложении с паддингами
		proper_sentence_start = window_size - middle_token_idx

		# Наши признаки - индексы словоформ, массивы индексов префиксов и индексов суффиксов длины RELEVANT_CHARS_SIZE,
		# индексы шаблонов капитализации. Также получаем метки токенов.
		word_indices = np.array([word2idx['PADDING_TOKEN']] * (2 * window_size + 1))
		# Считаем, что паддинги состоят из RELEVANT_CHARS_SIZE символов PADDING_TOKEN, которые не встречаются
		# нигде кроме паддингов
		pad_chars = [char2idx['PADDING_TOKEN']] * RELEVANT_CHARS_SIZE
		beginning_char_indices = np.array([pad_chars] * (2 * window_size + 1))
		ending_char_indices = np.array([pad_chars] * (2 * window_size + 1))
		case_indices = np.array([case2idx['PADDING_TOKEN']] * (2 * window_size + 1))
		label_indices = np.array([label2idx['Padding']] * (2 * window_size + 1))

		for pos_in_sentence, word in enumerate(sentence):

			token_unknown, word_idx, beginning_char_idxs, ending_char_idxs, case_idx = \
				get_token_indices(word, word2idx, char2idx, case2idx)

			pos_in_padded_sentence = pos_in_sentence + proper_sentence_start
			word_indices[pos_in_padded_sentence] = word_idx
			beginning_char_indices[pos_in_padded_sentence] = beginning_char_idxs
			ending_char_indices[pos_in_padded_sentence] = ending_char_idxs
			case_indices[pos_in_padded_sentence] = case_idx
			# Метки находятся во второй колонке корпуса в CoNLL- форамте
			if len(word) != 2:
				print('wrongtoken: "%s", in sentence "%s"' % (sentence, word))
			label_indices[pos_in_padded_sentence] = label2idx[word[LABEL_INDEX]]

			# Хотим вычислить процент словоформ, не покрываемых эмьеддингами
			total_tokens += 1
			if token_unknown:
				unknown_tokens += 1

		# Все данные для одного предложения помещаем в один массив
		dataset.append([word_indices, beginning_char_indices, ending_char_indices, case_indices, label_indices])
	#print(dataset[:5])
	percent = 0.0
	if total_tokens != 0:
		percent = float(unknown_tokens) / total_tokens * 100
	print("{} tokens, {} unknown, {:.3}%".format(total_tokens, unknown_tokens, percent ))
	return dataset
'''