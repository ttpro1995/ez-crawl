from src import BUWrapper

if __name__ == "__main__":
    url = "http://xuongmaythienphuc.vn"
    wrapper = BUWrapper(url)
    main_content = wrapper.get_main_content()
    # record_urls = list(set([Parser.get_text(record) for record in main_content]))
    for record in main_content:
        print(list(record.itertext()))
    print(len(main_content))