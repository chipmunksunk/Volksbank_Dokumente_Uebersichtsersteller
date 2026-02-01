categories_to_name_dict = {
    'Lebensmittel' : ['Aldi',
                      'Rewe',
                      ],
    'Einnahmen' : ['Gehalt',
                ],
}

name_to_categories_dict = {}
for category, name_list in  categories_to_name_dict.items():
    for name in name_list:
        name_to_categories_dict[name] = category