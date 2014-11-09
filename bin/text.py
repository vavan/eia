import re

        
class Text:
    pass

class TextProcessor:
    UKRAINIAN = 0
    ENGLISH = 1
    
    def __init__(self, base_folder = ''):
        self.language = 0
        self.__strings = {}
        self.__parse(base_folder)
    
    def __parse(self, base_folder = ''):
        strings = file(base_folder + 'strings.txt').read().splitlines()
        for line in strings:
            line = line.split(';')
            self.__strings[ line[0] ] = line[1:]
            
    def get_language(self, language):
        t = Text()
        for name, value in self.__strings.iteritems():
            setattr(t, name, value[language])
        return t


    

if __name__ == "__main__":
    s = TextProcessor().get_language(1)
    print s.RATE_TRAFBASED
