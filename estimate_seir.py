import os
import pandas as pd
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import minimize
import datetime as dt

dir_org = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_org) #作業フォルダの移動
sdate = dt.datetime.strptime("2013-01-01", "%Y-%m-%d") #始期
edate = dt.datetime.strptime("2020-10-23", "%Y-%m-%d") #終期
f_name = "tmp.csv"

t_max = 360 #終期（日）
dt = 0.01 #刻み幅
N = 126_000_000 #母集団の人数



#define differencial equation of seir model
def eq_seir(v, t, R_n0, epsilon, gamma, N):
  '''
  dS/dt = -beta * S * I / N
  dE/dt =  beta * S * I / N - epsilon * E
  dI/dt =  epsilon * E - gamma * I
  dR/dt =  gamma * I
  [v[0], v[1], v[2], v[3]]=[S, E, I, R]
  tはodeint用の引数
  '''
  beta = R_n0 / gamma
  dS = -beta*v[0]*v[2]/N
  dE = beta*v[0]*v[2]/N-epsilon*v[1]
  dI = epsilon*v[1]-gamma*v[2]
  dR = gamma*v[2]
  return [dS,dE,dI,dR]

def est_seir(t_max, dt, init_state, R_n0, epsilon, gamma, N):
  t = np.arange(0,t_max,dt)
  # 常微分方程式を解いて、len(t)*4の行列を出力する
  return odeint(eq_seir, ini_state, t, args=(R_n0, epsilon, gamma, N))

def loss_func(var, args):
  ini_state, R_n0 = var[0], var[1]
  latency_period, infectious_period = var[2], var[3]
  t_max, dt, N, target = args[0], args[1], args[2], args[3]
  # parameters
  epsilon = 1/latency_period #発症率
  gamma = 1/infectious_period #回復(or死亡)率
  return np.mean((target - est_seir(t_max, dt, init_state, R_n0, epsilon, gamma, N)[:,[2,3]])**2)


data = pd.read_csv(f_name, encoding="cp932",
                   index_col=0, parse_dates=True)
data = data.loc[sdate:edate,:]

# initial_state
# 10/1日時点
S_0 = N.copy()
I_0 = 84_285
E_0 = I_0.copy()
R_0 = 1_582
R_n0 = 1 #基本再生産数
latency_period_ini = 2 #潜伏期間
infectious_period_ini = 7.4 #感染期間

ini_vars = [[S_0, E_0, I_0, R_0],
             R_n0
             latency_period_ini,
             infectious_period_ini]



