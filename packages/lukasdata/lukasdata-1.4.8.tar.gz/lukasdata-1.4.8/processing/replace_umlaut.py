def replace_umlaut(iterable):
    new_list=[]
    umlaut_dict={"ä":"ae","ö":"oe","ü":"ue"}
    for item in iterable:
        if isinstance(item,str):
            for umlaut,replacement in umlaut_dict.items():
                item=item.replace(umlaut,replacement)
        new_list.append(item)
    return new_list
