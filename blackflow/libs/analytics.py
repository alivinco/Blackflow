__author__ = 'alivinco'

class AppAnalytics:
    def __init__(self):
        # every item is ["src","dst",value]
        self.link_couters = []

    def tick_link_counter(self,src,dst):
        r = filter(lambda lc_item:lc_item[0]==src and lc_item[1]==dst,self.link_couters)
        if len(r)>0:
            r[0][2]+=1
        else:
            self.link_couters.append([src,dst,1])
    def get_all_link_counters(self):
        return self.link_couters


# a = AppAnalytics()
# a.tick_link_counter("n1","n2")
# a.tick_link_counter("n1","n2")
# a.tick_link_counter("n1","n3")
# print a.get_all_link_counters()