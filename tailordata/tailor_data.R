# README
# やること
# 1. 全角数字を半角に、全角空白を半角に
# 2. それぞれのkeyに対してuniqueなvalueを調べて統一

library(tidyverse)

class_data <- read_csv('../scraping/test/csv/class_copy.csv')
glimpse(class_data)
