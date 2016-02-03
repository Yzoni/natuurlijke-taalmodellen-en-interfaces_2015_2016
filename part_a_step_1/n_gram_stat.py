import argparse

def get_text_as_list(filename):
    text_string = ""
    with open(filename, 'r') as f:
        for line in f:
            text_string += line
    f.close()
    #text_string = " ".join(re.findall("[a-zA-Z]+", st))
    text_list = text_string.split()
    return text_list

def find_n_grams(text_list, n):
    frequency_dict = {}
    for i in range(len(text_list)):
        n_gram = text_list[i:i+n]
        if len(n_gram) < n:
            break
        if str(n_gram) in frequency_dict:
            continue
        frequency_counter = 0
        for j in range(len(text_list)):
            sub_list = text_list[j:j+n]
            if n_gram == sub_list:
                frequency_counter += 1

        frequency_dict[str(n_gram)] = frequency_counter
    return frequency_dict

def get_most_frequent(frequency_dict,m):
    frequency_list = sorted(frequency_dict.items(), key=lambda x:x[1])
    return frequency_list[-m:]

def most_frequent_to_file(m_most_frequent_n_grams,n,corpus, m):
    filename =corpus + "_most_frequent_" + "n" + "_" + n + "_" + "m" + m +".txt"
    with open(filename, 'w+') as f:
        for n_gram in m_most_frequent_n_grams:
            f.write(str(n_gram) + "\n")
    f.close()
    return filename

def sum_frequencies_to_file(frequencies,corpus):
    filename = corpus + "_sum_frequencies" + ".txt"
    with open(filename, 'w+') as f:
        for frequency in frequencies:
            f.write(str(frequency) + "\n")
    f.close()
    return filename

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-n', type=int, nargs='?',help='n-grams', required=True)
    parser.add_argument('-corpus', help='corpus',nargs='?',required=True)
    parser.add_argument('-m', type=int, help='m most frequent',nargs='?',required=True)
    args = parser.parse_args()
    text_list = get_text_as_list(args.corpus)
    frequencies = []
    for i in range(1,2):
        frequency_dict = find_n_grams(text_list, i)
        m_most_frequent_n_grams = get_most_frequent(frequency_dict, args.m)
        wfilename = most_frequent_to_file(m_most_frequent_n_grams,str(i),args.corpus, str(args.m))
        print("wrote " + wfilename)
        frequencies.append((i, sum(frequency_dict.values())))
    wfilename = sum_frequencies_to_file(frequencies,args.corpus)
    print("wrote " + wfilename)
