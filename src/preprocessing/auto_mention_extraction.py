import argparse
import os
import pickle
from allennlp.predictors.predictor import Predictor
import logging




predictor = Predictor.from_path("https://s3-us-west-2.amazonaws.com/allennlp/models/elmo-constituency-parser-2018.03.14.tar.gz")


def get_root_of_mention(root, mention):
    for child in root['children']:
        if mention == child['word']:
            return child
        elif mention in child['word']:
            root = child

    print('No root matched for the mention: {}'.format(mention))
    return None


def main(args):
    num_sentences = 0
    for topic in os.listdir(args.raw_data):
        constituency_tree = {}
        logger.info('Processed topic {}'.format(topic))
        with open(os.path.join(args.raw_data, topic), 'r') as f_r:
            for line in f_r:
                if not line.strip():
                    continue
                elif line.strip().endswith('xml'):
                    corpus_file = line.strip()
                    constituency_tree[corpus_file] = []
                    logger.info('Processed file: {}'.format(corpus_file))
                else:
                    logger.info('Processed sentence num: {}'.format(line.split(' ')[0]))
                    sent = ' '.join(line.split(' ')[1:])
                    tree = predictor.predict(sentence=sent)
                    constituency_tree[corpus_file].append(tree['hierplane_tree']['root'])
                    num_sentences += 1

        with open(os.path.join(args.output_path, topic), 'wb') as f_w:
            pickle.dump(constituency_tree, f_w)

    logger.info('{} sentences were processed'.format(num_sentences))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw_data', type=str, default='ecb_raw_data')
    parser.add_argument('--output_path', type=str, default='ecb_constituency_tree')
    args = parser.parse_args()

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=os.path.join(args.output_path, "allen_constituency_tree.txt"),
                        level=logging.DEBUG, filemode='w', datefmt='%Y-%m-%d %H:%M:%S')
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger(__name__)

    main(args)

