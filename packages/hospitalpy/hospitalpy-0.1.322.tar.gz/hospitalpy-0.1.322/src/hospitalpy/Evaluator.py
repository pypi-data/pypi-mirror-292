class Evaluator:
    def __init__(self, filename=None, data=None):
        self.filename = filename
        self.data = data

        if filename:
            pass
        elif data and not filename:
            pass
        elif data and filename:
            pass
        else:
            raise Exception('No data provided.')


    def evaluate_single(self, Toker, gold_standard=None):
        print('Evaluating single...')

        original = Toker.aStr
        processed = Toker.standardized

        print(f'Original: {original}')
        print(f'Processed: {processed}')

        if gold_standard:
            print(f'Gold Standard: {gold_standard}')

    def evaluate(self):
        pass
        # data format: [original, standardized, gold_standard]

