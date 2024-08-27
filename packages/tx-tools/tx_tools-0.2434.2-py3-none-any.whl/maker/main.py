from maker.fuzzy_maker import FuzzyMaker


def main():
    maker = FuzzyMaker()
    cmd = maker.run()
    print(cmd or '')


if __name__ == "__main__": main()
