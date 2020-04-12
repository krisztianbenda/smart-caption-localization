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

    def get_start_time_milliseconds(self) -> float:
        t = self.srt[self.current_block].start.to_time()
        return ((t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond/1000
