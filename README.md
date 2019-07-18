- [Instruction](#Instruction)
- [Functions details in utils.py](#Functions-details-in-utilspy)
  - [get_firm_uid(header_uids: dict, name_list: list) -> List[str]](#getfirmuidheaderuids-dict-namelist-list---Liststr)
  - [get_basic_info_soup(header_basic_info: dict, uid_list: list) -> List[BeautifulSoup]](#getbasicinfosoupheaderbasicinfo-dict-uidlist-list---ListBeautifulSoup)
  - [get_dev_info_soup(header_dev_info: dict, uid_list: list) -> List[BeautifulSoup]](#getdevinfosoupheaderdevinfo-dict-uidlist-list---ListBeautifulSoup)
  - [parse_basic_info(basic_soup: BeautifulSoup) -> dict](#parsebasicinfobasicsoup-BeautifulSoup---dict)
  - [parse_dev_info(dev_soup: BeautifulSoup) -> dict](#parsedevinfodevsoup-BeautifulSoup---dict)
  - [fill_excel(path_to_sample_file: str, output_dir: str, all_df: pd.DataFrame) -> None](#fillexcelpathtosamplefile-str-outputdir-str-alldf-pdDataFrame---None)
- [To do](#To-do)

## Instruction


This crawler is designed for specific use case, you can find that I only parsed some specific information. However the code's logic is easy to read and you can customize it to meet you personal demand.

- This crawler use cookies to authenticate login
- Please check the function in `utils.py` which includes all core codes

## Functions details in utils.py

### get_firm_uid(header_uids: dict, name_list: list) -> List[str]

This function takes:

```python
# @header_uids: a header dictionary for requests
# @name_list: a list of company names

# @return: a list of company's uid
```

The uid acts as a Unique Identifier for a company, it is assigned for every company by qichacha, we need that uid to get the specific website for each company.

### get_basic_info_soup(header_basic_info: dict, uid_list: list) -> List[BeautifulSoup]

```python
# @header_basic_info: a header dictionary for request basic info
# @uid_list: a list of company's uid

# @preturn: a list of BeautifulSoup instance, which contains the basic info page htlm contents
```

This function is used for fetching the basic information for a company. Specifically, there are two main pages I want to parse, one is the basic information page (基本信息 in chinese), another is development page (企业发展 in chinese). So, the function just fetch the basic information page html content.

### get_dev_info_soup(header_dev_info: dict, uid_list: list) -> List[BeautifulSoup]

```python
# @header_dev_info: a header dictionary for request development info
# @uid_list: a list of company's uid

# @preturn: a list of BeautifulSoup instance, which contains the development info page htlm contents
```

This function is used for fetching the development information for a company as I metion above.

### parse_basic_info(basic_soup: BeautifulSoup) -> dict

```python
# @basic_soup: a list of BeautifulSoup instance, which contains the basic info page htlm contents

# @preturn: a dictionary that contains selected basic information. key is the name of info, value is the value of that info. E.g. "website": "www.example.com"
```

### parse_dev_info(dev_soup: BeautifulSoup) -> dict

```python
# @dev_soup: a list of BeautifulSoup instance, which contains the development info page htlm contents

# @preturn: a dictionary that contains selected development information. key is the name of info, value is the value of that info. E.g. "total_profits": "xxx"
```

### fill_excel(path_to_sample_file: str, output_dir: str,  all_df: pd.DataFrame) -> None

```python
# @path_to_sample_file: path to sample excel form file that you want to fill
# @output_dir: output directory
# @all_df: the pandas.DataFrame that contains all information, each row corresponds to each company, columns is the name of info
```

## To do

For the future, maybe I will write a cli wraper for this crawler, let's see.