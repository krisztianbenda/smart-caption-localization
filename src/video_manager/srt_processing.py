import pysrt
import time

class SRTHandler:
    def __init__(self, srt_file):
        self.srt = pysrt.open(srt_file)
        self.current_block = 0

    def get_start_time(self):
        return self.srt[self.current_block].start.to_time()

    def get_text(self):
        return self.srt[self.current_block].text
    
    def next(self) -> bool:
        if self.current_block < len(self.srt) - 1:
            self.current_block += 1
            return True
        return False

    def get_end_time(self):
        return self.srt[self.current_block].end.to_time()

    def get_end_time_ms(self) -> float:
        t = self.srt[self.current_block].end.to_time()
        return ((t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond/1000

    def get_start_time_milliseconds(self) -> float:
        t = self.srt[self.current_block].start.to_time()
        return ((t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond/1000

    def get_middle_time_ms(self) -> float:
        return self.get_start_time_milliseconds() + (self.get_end_time_ms() - self.get_start_time_milliseconds())/2

    def get_block_number(self) -> int:
        return self.current_block

    def get_by_second(self, second) -> str:
        return self.srt.at(seconds=second).text
    
    # def get_block_by_second(self, second) -> int:
    #     for sub_num in range(0, len(self.srt)):
    #         start_time = self.srt[sub_num].start.to_time()
    #         print(start_time)
    #         start_time_sec = (start_time.hour * 60 + start_time.minute) * 60 + start_time.second + start_time.microsecond/1000/1000
    #         print(start_time_sec)
    #         end_time = self.srt[sub_num].end.to_time()
    #         print(end_time)
    #         end_time_sec = (end_time.hour * 60 + end_time.minute) * 60 + end_time.second + end_time.microsecond/1000/1000
    #         print(end_time_sec)
    #         if start_time_sec <= second and second < end_time_sec:
    #             print("returning with: {}".format(sub_num))
    #             return sub_num
    #     return -1