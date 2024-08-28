#!/usr/bin/env python
em=True
eY=str
es=len
ew=print
eO=enumerate
eH=int
eI=range
eB=False
import argparse
g=argparse.ArgumentParser
from pathlib import Path
import calib
a=calib.update_info_mz
x=calib.update_info_im
b=calib.update_info_rt
import fdr
K=fdr.cal_q_pro_pg
c=fdr.cal_q_pr_second
V=fdr.filter_by_q_cut
U=fdr.adjust_rubbish_q
v=fdr.cal_q_pr_first
import quant
n=quant.quant_pg
z=quant.quant_pr
import scoring
X=scoring.update_scores
l=scoring.score_locus
from decoy import make_decoys,cal_fg_mz_iso
from library import Library
from main_core import*
from refine import refine_models
from tims import Tims
try:
 e
except:
 e=lambda x:x
m=p.get_logger()
def i():
 Y=g('Beta-DIA for diaPASEF analysis')
 Y.add_argument('-ws','--ws',required=em,help='specify the folder that is .d or contains .d files.')
 Y.add_argument('-lib','--lib',required=em,help='specify the absolute path of a .speclib spectra library.')
 Y.add_argument('-out_name','--out_name',type=eY,default='beta_dia',help='specify the folder name of outputs.')
 w=Y.parse_args()
 return Path(w.ws),Path(w.lib),w.out_name
def h(ws):
 O=[]
 if ws.suffix=='.d':
  O.append(ws)
 else:
  for H in ws.rglob('*.d'):
   if H.is_dir():
    O.append(H)
 I.multi_ws=O
 I.file_num=es(I.multi_ws)
def D(H,total,ws,B):
 I.ws=ws
 I.dir_out=(ws/B)
 I.dir_out.mkdir(exist_ok=em)
 p.set_logger(I.dir_out,is_time_name=I.is_time_log)
 m.info(f'====================={ws_i+1}/{total}=====================')
 m.info('Workspace is: '+eY(ws))
def F(ws):
 ms=Tims(I.ws)
 E=ms.get_device_name()
 M=ms.get_scan_rts()[-1]/60.
 m.info('tims_name: {}, gradient: {:.2f}min'.format(E,M))
 utils.get_diann_info(ws)
 return ms
@e
def W():
 y=torch.cuda.get_device_properties(0).total_memory
 if y/1024**3<10:
  ew('GPU memory is less than 10G! Beta-DIA exits!')
  return
 ws,S,B=i()
 h(ws)
 o=Library(S,worker_num=1 if __debug__ else 8)
 for H,ws in eO(I.multi_ws):
  D(H,I.file_num,ws,B)
  ms=F(I.ws)
  I.tol_rt=ms.get_scan_rts()[-1]*I.tol_rt_ratio
  L=np.diff(ms.get_scan_rts()).mean()
  I.locus_rt_thre=L*I.locus_valid_num
  T=o.polish_lib(ms.get_swath(),)
  m.info('targets num: {}'.format(es(T)))
  P,u=deepmap.load_models()
  cal_recall_seek_seed(T,ms,P)
  j=seek_seed(T,ms,P)
  utils.save_as_pkl(j,'df_seed.pkl')
  j,T=b(j,T)
  j,T=x(j,T)
  j=a(j,ms)
  f(T,ms,P,tol_rt=I.tol_rt,top_sa_cut=I.top_sa_cut,top_deep_cut=I.top_deep_cut,)
  A=eH(np.ceil(es(T)/I.target_batch_max))
  d=np.array_split(T.index.values,A)
  t=[]
  for R in eI(es(d)):
   if R%2==0:
    m.disabled=eB
    G='-------------File-{}/{}-Batch-{}/{}------------'.format(H+1,I.file_num,R+1,A)
    m.info(G)
   else:
    m.disabled=em
   df=T.iloc[d[R]].reset_index(drop=em)
   Q=make_decoys(df,I.fg_num,method='mutate')
   df=pd.concat([df,Q]).reset_index(drop=em)
   df=seek_locus(df,ms,P,I.top_sa_cut,I.top_deep_cut)
   df=cal_fg_mz_iso(df)
   df=l(df,ms,P,u)
   if R==0:
    df,C=v(df,50,24)
    r=U(df,A)
    df=V(df,r)
   else:
    df,C=v(df,50,24,C)
    df=V(df,r)
   t.append(df)
  df=pd.concat(t,axis=0,ignore_index=em)
  df=o.assign_proteins(df)
  m.disabled=eB
  m.info('--------------------Concat batches:---------------------')
  df,_=v(df,50,12)
  df=V(df,1)
  m.info('--------------------------------------------------------')
  utils.save_as_pkl(df,'df_scores1.pkl')
  P,u,J=refine_models(df,ms,P,u)
  df=X(df,ms,P,u,J)
  utils.save_as_pkl(df,'df_scores2.pkl')
  df=c(df,50,8)
  utils.save_as_pkl(df,'df_fdr1.pkl')
  df=K(df,I.inference_q_cut)
  utils.save_as_pkl(df,'df_fdr2.pkl')
  df=df[df['q_pr']<0.05].reset_index(drop=em)
  df=z(df,ms)
  utils.save_as_pkl(df,'df_quant1.pkl')
  df=n(df)
  df=utils.convert_cols_to_diann(df)
  utils.save_as_tsv(df,'report_beta.tsv')
  del T,df,ms
  m.info('Finished.')
if __name__=='__main__':
 W()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
