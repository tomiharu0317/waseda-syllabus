# README
# やること
# 1. 全角数字を半角に、全角空白を半角に
# 2. それぞれのkeyに対してuniqueなvalueを調べて統一

library(tidyverse)

class_data <- read_csv('../scraping/data/copy/class_1_copy.csv')
glimpse(class_data)
head(class_data)
unique(class_data$開講年度)
unique(class_data$単位数)
unique(class_data$キャンパス)
unique(class_data$開講箇所)
unique(class_data$学期曜日時限)
unique(class_data$授業方法区分)
