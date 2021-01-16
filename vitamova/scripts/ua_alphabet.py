def is_ua_letter(letter):
    all_letters = "АаБбВвГгҐґДдЕеЄєЖжЗзИиІіЇїЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЬьЮюЯя'"
    if letter in all_letters:
        return True
    else:
        return False

#This function splits up a text of ukrainian words into a list of those words without any white space or punctuation.
def split_word_list(text):
    result_list = []
    word = ""
    for char in text:
        is_ua = is_ua_letter(char)
        if is_ua:
            word += char
        else:
            if word != "":
                result_list.append(word)
                word = ""
    return result_list
