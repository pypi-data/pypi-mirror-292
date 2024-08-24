import unittest
from unittest.mock import patch
from jgtml.SignalOrderingHelper import valid_gator,is_bar_out_of_mouth,is_mouth_open

import pandas as pd

#The Last two rows of the CSV file:
AUDCAD_H1_24082111_CSV_ROWS="""
2024-08-21 10:00:00,0.91687,0.91728,0.91635,0.91691,0.91696,0.91735,0.91642,0.91698,3348,0.916915,0.917315,0.916385,0.916945,0.91685,-0.04131217738,-0.16660641799,0.91789748219,0.91834963993,0.91826803675,0.90710133862,0.91091454742,0.91403437288,0.91014196311,0.90620074471,0.90529160356,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.02777777778,1,0,1,0,1,0.0,0.0,0.0,red,-1.0,1.0,0.0,0.0,0.0,0.0,0.0,0,0,0,0,0,0,0,1,2,-+
2024-08-21 11:00:00,0.91691,0.91692,0.91646,0.9166,0.91698,0.91699,0.91655,0.91667,1667,0.916945,0.916955,0.916505,0.916635,0.91673,-0.07513993595,-0.18265915233,0.9179434451,0.91833030994,0.9180054294,0.90717694156,0.91103191928,0.91418247956,0.9101070839,0.90620436812,0.90530824173,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.02699460108,0,0,0,0,1,0.0,0.0,0.0,red,-1.0,1.0,0.0,0.0,0.0,0.0,0.0,0,0,0,0,0,0,1,0,3,--

"""
from SOHelper import get_last_two_bars

AUD_CAD_H1_cds_cache_24081918_mouth_open_sell_no_ao_divergence="AUD-CAD_H1_cds_cache_24081918_mouth_open_sell_no_ao_divergence.csv"

EUR_JPY_H1_cds_cache_240821="EUR-JPY_H1_cds_cache__24082112.csv"

mouth_closed_samples=[
  {
    "fn":EUR_JPY_H1_cds_cache_240821,
    "date_from":"2024-08-21 05:00:00",
    "expected":False
  },
  {
    "fn":EUR_JPY_H1_cds_cache_240821,
    "date_from":"2024-08-20 23:00:00",
    "expected":True
  }]

fdb_samples=[
  {
    "fn":EUR_JPY_H1_cds_cache_240821,
    "date_from":"2024-08-20 23:00:00",
    "expected":True
  }]

_FDB_DIR="tests/fdb_data"#

class TestCDSBase(unittest.TestCase):
  def read_last_two_bars(self, fn):
      data=self._read_cds_df(fn)
      last_bar_completed,current_bar = get_last_two_bars(data)
      return last_bar_completed,current_bar

  def __mksamplepath(self,fn):
    return f"{_FDB_DIR}/{fn}"
  
  def _read_cds_df(self,fn):
    fpath=self.__mksamplepath(fn)
    data=pd.read_csv(fpath,index_col=0,parse_dates=True)
    return data
  
  def _read_cds_df_from_dt(self,fn,date_from):
    data=self._read_cds_df(fn)
    filtered_data = data.loc[date_from:]
    return filtered_data
  
  def getbars_from_date_from(self,fn,date_from):
    data=self._read_cds_df_from_dt(fn,date_from)
    last_bar_completed,current_bar = get_last_two_bars(data)
    return last_bar_completed,current_bar
  
  def getbars_sample_mouth_closed(self,index = 0):    
    sample=mouth_closed_samples[index]
    fn=sample["fn"]
    date_from=sample["date_from"]
    expected=sample["expected"]
    last_bar_completed,current_bar=self.getbars_from_date_from(fn,date_from)
    return last_bar_completed,current_bar
  
  def _getbars_mouth_is_open_sell__240821(self):
    fn = AUD_CAD_H1_cds_cache_24081918_mouth_open_sell_no_ao_divergence
    last_bar_completed,current_bar=self.read_last_two_bars(fn)
    return last_bar_completed,current_bar
  
class TestValidGator(TestCDSBase):

  def test_is_mouth_open_sell_returns_true(self):
    #fn = AUD_CAD_H1_cds_cache_24081918_mouth_open_sell_no_ao_divergence
    last_bar_completed,current_bar=self._getbars_mouth_is_open_sell__240821()#self.read_last_two_bars(fn)
    bar_is_open_result=is_mouth_open(last_bar_completed,"S")
    self.assertTrue(bar_is_open_result)
    
    last_bar_completed,current_bar=self.getbars_sample_mouth_closed(1)
    bar_is_open_result=is_mouth_open(last_bar_completed,"S")    
    self.assertTrue(bar_is_open_result)
     
    
    
    
  def test_is_mouth_open_buy_returns_false(self):
    last_bar_completed,current_bar=self._getbars_mouth_is_open_sell__240821()
    bar_is_open_result=is_mouth_open(last_bar_completed,"B")
    self.assertFalse(bar_is_open_result)
    
    #2nd sample
    last_bar_completed,current_bar=self.getbars_sample_mouth_closed(0)
    bar_is_open_result=is_mouth_open(last_bar_completed,"B")
    
    self.assertFalse(bar_is_open_result)
    
    

  # def read_last_two_bars(self, fn):
  #     data=self._read_cds_df(fn)
  #     last_bar_completed,current_bar = get_last_two_bars(data)
  #     return last_bar_completed,current_bar

  # def _read_cds_df(self,fn):
  #   data=pd.read_csv(fn,index_col=0,parse_dates=True)
  #   return data
  
  def test_valid_gator_returns_true(self):
    
    #data=pd.read_csv(pd.compat.StringIO(AUDCAD_H1_24082111_CSV_ROWS),header=None)
    data = pd.read_csv('tests/fdb_data/AUD-CAD_H1_cds_cache_24082107.csv')
    
    
    last_bar_completed,current_bar = get_last_two_bars(data)
    
    bs = "B"

    result = valid_gator(last_bar_completed, current_bar, bs)

    self.assertTrue(result)

  def test_valid_gator_returns_false(self):
    last_bar_completed = {
      'HIGH': 0.91735,
      'LOW': 0.91642,
      'FDB': 0,
      'ASKHIGH': 0.91789748219,
      'BIDLOW': 0.91014196311,
      'JAW': 0.90529160356,
      'TEETH': 0.90529160356,
      'LIPS': 0.90529160356
    }
    current_bar = {
      'HIGH': 0.91698,
      'LOW': 0.91667,
      'FDB': 0,
      'ASKHIGH': 0.9179434451,
      'BIDLOW': 0.9101070839,
      'JAW': 0.90530824173,
      'TEETH': 0.90530824173,
      'LIPS': 0.90530824173
    }
    bs = "S"

    result = valid_gator(last_bar_completed, current_bar, bs)

    self.assertFalse(result)

if __name__ == "__main__":
  unittest.main()