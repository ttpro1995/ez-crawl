from lxml import etree
import lxml.html
from src.utils import *
from lxml.html.clean import Cleaner
from collections import defaultdict
from selenium import webdriver
from pyvirtualdisplay import Display
from collections import Counter

class BUWrapper(object):

    def __init__(self, url):
        self.url = url

        self.root = self.construct_tree()
        self.tree = etree.ElementTree(self.root)

        self.leaf_nodes = []
        get_all_leaf_nodes(self.root, self.leaf_nodes)

    def construct_tree(self):
        doc = self.get_data()
        root = lxml.html.fromstring(doc)
        return root

    def construct_items(self):
        paths = [self.get_simplified_path(node) for node in self.leaf_nodes]
        items = [node for node in self.leaf_nodes
                 if paths.count(self.get_simplified_path(node)) >= 3]
        return items

    def group_by_path(self, node_list):
        """
        :param node_list: list of HtmlElement nodes
        :return: dict with key be simple path of nodes, value be list of node with the same simple path
        """
        grp = defaultdict(list)
        for node in node_list:
            key = self.get_simplified_path(node)
            grp[key].append(node)
        return grp

    def find_region_candidates(self):
        records = self.get_data_records()
        grp = self.group_by_path(records)
        return grp

    def get_data(self):
        # display = Display()
        # display.start()
        driver = webdriver.Firefox()
        driver.get(self.url)
        html_body = driver.page_source

        cleaner = Cleaner()
        doc = cleaner.clean_html(html_body)
        return doc

    def get_simplified_path(self, node):
        return re.sub(pattern, '', self.tree.getpath(node))

    def find_record_candidates(self):
        items = self.construct_items()
        grp_items = self.group_by_path(items)
        candidates = []
        for path in list(grp_items.keys()):
            for node in grp_items[path]:
                candidates.extend(check_record_candidate(node, grp_items[path]))
        return list(set(candidates))

    def get_data_records(self):
        """
        Filter out all data records that has only one data item (global) and less than 3 simplified path
        """
        items = self.construct_items()
        records = self.find_record_candidates()

        paths = [self.get_simplified_path(record) for record in records]
        records = [record for record in records
                   if count_descendants(record, items) > 1 and
                   paths.count(self.get_simplified_path(record)) >= 5]

        return records

    def get_main_content(self):
        """
        Idea:
        1. Find the largest text block from each record in each region
        2. Measure entropy for each region based on largest text blocks size
        3. Main content is the block with maximum entropy
        """
        grp_regions = self.find_region_candidates()
        d_entropy = Counter()
        for path in list(grp_regions.keys()):
            region = grp_regions[path]
            text_lens = []
            for record in region:
                text_lens.append(len(get_largest_text(record))) # Step 1
            entropy = compute_entropy(text_lens) # Step 2
            d_entropy[path] = entropy

        main_region_path = d_entropy.most_common(1)[0][0] # Step 3
        return grp_regions[main_region_path]


if __name__ == '__main__':
    wrapper = BUWrapper('https://www.amazon.com/s/?rh=n%3A7141123011%2Cn%3A10445813011%2Cn%3A7147440011%2Cn%3A1040660%2Cn%3A1045024&bbn=10445813011&pf_rd_p=d5e6f04b-1f69-4f23-ae52-0c166e61cfd5&pf_rd_r=K2JX835YX15YYPPS06T6')
    # wrapper = BUWrapper('https://nha.chotot.com')
    # grp = wrapper.find_region_candidates()
    # for path in list(grp.keys()):
    #     print('<<<<')
    #     for item in grp[path]:
    #         print(etree.tostring(item))
    #     print('>>>>')
    main_content = wrapper.get_main_content()
    for item in main_content:
        print(etree.tostring(item))