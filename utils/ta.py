import pandas as pd
import numpy as np

def get_sma(indicator, prices, col, window) :
    prices[col]  = prices[col].rolling(window=window).mean()
    prices['id'] = indicator + "_" + str(window)
    prices["chart_category"] = "price"
    prices[col] = prices[col]
    return prices

def get_rsi(indicator, prices, col, window) :
    delta = prices[col].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    RS = gain / loss
    RSI = 100 - (100 / (1 + RS))
    prices['id'] = indicator + "_" + str(window)
    prices[col] = RSI / 100
    prices["chart_category"] = "purcentage_positive"
    prices[col] = prices[col]
    return prices

def get_macd(indicator, prices, col, short_window, long_window, span=9) :
        short_ema = prices[col].ewm(span=short_window, adjust=False).mean()
        long_ema = prices[col].ewm(span=long_window, adjust=False).mean()
        macd = short_ema - long_ema
        prices[col] = macd.ewm(span=span, adjust=False).mean()
        prices['id'] = indicator + "_" + str(short_window) + "_" + str(long_window) + "_" + str(span)
        prices["chart_category"] = "purcentage"
        return prices

def get_std(indicator, prices, col, window) :
    prices['id'] = indicator + "_" + str(window)
    prices["chart_category"] = "purcentage_positive"
    prices[col] = prices[col].rolling(window=window).std()
    return prices

def get_bollinger_bands(indicator, prices, col, window) :
    ma = get_sma(indicator, prices.copy(), col, window)
    std = get_std(indicator, prices.copy(), col, window)
    bb_up = prices.copy()
    bb_down = prices.copy()
    for i in range(len(ma)):
        bb_up[col][i] = ma[col][i] + 2 * std[col][i] 
        bb_down[col][i] = ma[col][i]  - 2 * std[col][i] 
    bb_up['id'] = indicator + "_up_" + str(window)
    bb_up["chart_category"] = "price"
    bb_down['id'] = indicator + "_down_" + str(window)
    bb_down["chart_category"] = "price"
    bb = pd.concat([bb_up, bb_down])
    return bb

def get_ema(indicator, prices, col, window):
    prices[col] = prices[col].ewm(span=window, adjust=False).mean()
    prices['id'] = indicator + "_" + str(window)
    prices["chart_category"] = "price"
    return prices
            
            # self.data[symbol + '_EMA' + str(self.window)] = np.zeros(len(self.data[symbol]))
            # if symbol + '_SMA' + str(self.window) not in self.data.columns:
            #     self.get_sma()
            # self.data[symbol + '_EMA' + str(self.window)][self.window - 1] = np.mean(self.data[symbol + '_SMA' + str(self.window)][:self.window])
            # for i in range(self.window, len(self.data[symbol])):
            #     self.data[symbol + '_SMA' + str(self.window)][i] = (self.data[symbol + '_SMA' + str(self.window)][i] * (self.smoothing / (1 + self.window))) + (self.data[symbol + '_SMA' + str(self.window)][i - 1] * (1 - (self.smoothing / (1 + self.window))))


def get_tr(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_TR'] = self.data[symbol]['high'] - self.data[symbol]['low']
            
def get_atr(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            if symbol + '_TR' not in self.data.columns :
                self.get_tr()
            self.data[symbol + '_TR'] = self.data[symbol]['high'] - self.data[symbol]['low']
            self.data[symbol + '_ATR' + str(self.window)] = self.data[symbol + '_TR'].rolling(window=self.window).mean()

def get_stochastic_oscillator(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_low_' + str(self.window)] = self.data[symbol]['low'].rolling(window=self.window).min()
            self.data[symbol + '_high_' + str(self.window)] = self.data[symbol]['high'].rolling(window=self.window).max()
            self.data[symbol + '_SO'] = 100 * (self.data[symbol]['close'] - self.data[symbol + '_low_' + str(self.window)]) / (self.data[symbol + '_high_' + str(self.window)] - self.data[symbol + '_low_' + str(self.window)])
    
def get_momentum(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_MOM' + str(self.window)] = self.data[symbol]['close'].diff(self.window)

def get_williams_r(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_low_' + str(self.window)] = self.data[symbol]['low'].rolling(window=self.window).min()
            self.data[symbol + '_high_' + str(self.window)] = self.data[symbol]['high'].rolling(window=self.window).max()
            self.data[symbol + '_WR'] = -100 * (self.data[symbol + '_high_' + str(self.window)] - self.data[symbol]['close']) / (self.data[symbol + '_high_' + str(self.window)] - self.data[symbol + '_low_' + str(self.window)])
    
def get_cci(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_TP'] = (self.data[symbol]['high'] + self.data[symbol]['low'] + self.data[symbol]['close']) / 3
            self.data[symbol + '_CCI'] = (self.data[symbol + '_TP'] - self.data[symbol + '_TP'].rolling(window=self.window).mean()) / (0.015 * self.data[symbol + '_TP'].rolling(window=self.window).std())

def get_aroon(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_up_' + str(self.window)] = self.data[symbol]['high'].rolling(window=self.window).apply(lambda x: x.argmax())
            self.data[symbol + '_down_' + str(self.window)] = self.data[symbol]['low'].rolling(window=self.window).apply(lambda x: x.argmin())
            self.data[symbol + '_Aroon_up'] = 100 * (window - self.data[symbol + '_up_' + str(self.window)]) / window
            self.data[symbol + '_Aroon_down'] = 100 * (window - self.data[symbol + '_down_' + str(self.window)]) / window

def get_obv(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_OBV'] = np.where(self.data[symbol]['close'] > self.data[symbol]['close'].shift(1), self.data[symbol]['volume'], -self.data[symbol]['volume']).cumsum()

def get_mfi(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_TP'] = (self.data[symbol]['high'] + self.data[symbol]['low'] + self.data[symbol]['close']) / 3
            self.data[symbol + '_MF'] = self.data[symbol + '_TP'] * self.data[symbol]['volume']
            self.data[symbol + '_MF_pos'] = np.where(self.data[symbol]['close'] > self.data[symbol]['close'].shift(1), self.data[symbol + '_MF'], 0)
            self.data[symbol + '_MF_neg'] = np.where(self.data[symbol]['close'] < self.data[symbol]['close'].shift(1), self.data[symbol + '_MF'], 0)
            self.data[symbol + '_MFR'] = self.data[symbol + '_MF_pos'].rolling(window=self.window).sum() / self.data[symbol + '_MF_neg'].rolling(window=self.window).sum()
            self.data[symbol + '_MFI'] = 100 - 100 / (1 + self.data[symbol + '_MFR'])
    
def get_pivot_points(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_pivot'] = (self.data[symbol]['high'] + self.data[symbol]['low'] + self.data[symbol]['close']) / 3
            self.data[symbol + '_R1'] = 2 * self.data[symbol + '_pivot'] - self.data[symbol]['low']
            self.data[symbol + '_S1'] = 2 * self.data[symbol + '_pivot'] - self.data[symbol]['high']
            self.data[symbol + '_R2'] = self.data[symbol + '_pivot'] + self.data[symbol]['high'] - self.data[symbol]['low']
            self.data[symbol + '_S2'] = self.data[symbol + '_pivot'] - self.data[symbol]['high'] + self.data[symbol]['low']
            self.data[symbol + '_R3'] = self.data[symbol]['high'] + 2 * (self.data[symbol + '_pivot'] - self.data[symbol]['low'])
            self.data[symbol + '_S3'] = self.data[symbol]['low'] - 2 * (self.data[symbol]['high'] - self.data[symbol + '_pivot'])

def get_fibonacci_retracement(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_high'] = self.data[symbol]['high'].max()
            self.data[symbol + '_low'] = self.data[symbol]['low'].min()
            self.data[symbol + '_diff'] = self.data[symbol + '_high'] - self.data[symbol + '_low']
            self.data[symbol + '_R1'] = self.data[symbol + '_high'] - 0.236 * self.data[symbol + '_diff']
            self.data[symbol + '_R2'] = self.data[symbol + '_high'] - 0.382 * self.data[symbol + '_diff']
            self.data[symbol + '_R3'] = self.data[symbol + '_high'] - 0.618 * self.data[symbol + '_diff']
            self.data[symbol + '_S1'] = self.data[symbol + '_high'] - 0.236 * self.data[symbol + '_diff']
            self.data[symbol + '_S2'] = self.data[symbol + '_high'] - 0.382 * self.data[symbol + '_diff']
            self.data[symbol + '_S3'] = self.data[symbol + '_high'] - 0.618 * self.data[symbol + '_diff']

def get_trix(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_TRIX'] = self.data[symbol]['close'].ewm(span=self.window, adjust=False).mean().ewm(span=self.window, adjust=False).mean().ewm(span=self.window, adjust=False).mean()
            self.data[symbol + '_signal'] = self.data[symbol + '_TRIX'].ewm(span=9, adjust=False).mean()

def get_vortex(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_TR'] = self.data[symbol]['high'] - self.data[symbol]['low']
            self.data[symbol + '_TR'] = self.data[symbol + '_TR'].shift(1)
            self.data[symbol + '_TR'] = self.data[symbol + '_TR'].rolling(window=self.window).sum()
            self.data[symbol + '_VM_plus'] = abs(self.data[symbol]['high'] - self.data[symbol]['low'].shift(1))
            self.data[symbol + '_VM_minus'] = abs(self.data[symbol]['low'] - self.data[symbol]['high'].shift(1))
            self.data[symbol + '_VM_plus'] = self.data[symbol + '_VM_plus'].rolling(window=self.window).sum() / self.data[symbol + '_TR']
            self.data[symbol + '_VM_minus'] = self.data[symbol + '_VM_minus'].rolling(window=self.window).sum() / self.data[symbol + '_TR']

def get_kst(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            ROC_1 = self.data[symbol]['close'].diff(10)
            ROC_2 = self.data[symbol]['close'].diff(15)
            ROC_3 = self.data[symbol]['close'].diff(20)
            ROC_4 = self.data[symbol]['close'].diff(30)
            self.data[symbol + '_KST'] = (ROC_1.rolling(window=self.window).sum() + ROC_2.rolling(window=self.window).sum() * 2 + ROC_3.rolling(window=self.window).sum() * 3 + ROC_4.rolling(window=self.window).sum() * 4) / 6

def get_ichimoku_cloud(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_conversion'] = (self.data[symbol]['high'].rolling(window=9).max() + self.data[symbol]['low'].rolling(window=9).min()) / 2
            self.data[symbol + '_base'] = (self.data[symbol]['high'].rolling(window=26).max() + self.data[symbol]['low'].rolling(window=26).min()) / 2
            self.data[symbol + '_lead_a'] = (self.data[symbol + '_conversion'] + self.data[symbol + '_base']) / 2
            self.data[symbol + '_lead_b'] = (self.data[symbol]['high'].rolling(window=52).max() + self.data[symbol]['low'].rolling(window=52).min()) / 2

def get_fisher_transform(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_fisher'] = 0.5 * (np.log((1 + self.data[symbol]['close'].diff(1) / self.data[symbol]['close'].shift(1)) / 2) + self.data[symbol + '_fisher'].shift(1))

def get_chaikin_oscillator(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_CMF'] = ((self.data[symbol]['close'] - self.data[symbol]['low']) - (self.data[symbol]['high'] - self.data[symbol]['close'])) / (self.data[symbol]['high'] - self.data[symbol]['low'])
            self.data[symbol + '_CMF'] = self.data[symbol + '_CMF'].rolling(window=20).mean()

def get_parabolic_sar(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_SAR'] = np.zeros(len(self.data[symbol]))
            self.data[symbol + '_SAR'][0] = self.data[symbol]['high'][0]
            self.data[symbol + '_EP'] = self.data[symbol]['low'][0]
            self.data[symbol + '_AF'] = 0.02
            self.data[symbol + '_SAR'][1] = self.data[symbol + '_SAR'][0] - self.data[symbol + '_AF'] * (self.data[symbol + '_SAR'][0] - self.data[symbol + '_EP'])
            for i in range(2, len(self.data[symbol])) :
                if self.data[symbol]['high'][i] > self.data[symbol + '_SAR'][i - 1] :
                    self.data[symbol + '_EP'] = self.data[symbol]['high'][i]
                    self.data[symbol + '_AF'] = min(0.2, self.data[symbol + '_AF'] + 0.02)
                self.data[symbol + '_SAR'][i] = self.data[symbol + '_SAR'][i - 1] + self.data[symbol + '_AF'] * (self.data[symbol + '_EP'] - self.data[symbol + '_SAR'][i - 1])
                if self.data[symbol + '_SAR'][i] > self.data[symbol]['low'][i] :
                    self.data[symbol + '_SAR'][i] = self.data[symbol]['low'][i]
                    self.data[symbol + '_EP'] = self.data[symbol]['high'][i]
                    self.data[symbol + '_AF'] = 0.02

def get_keltner_channel(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_KC'] = (self.data[symbol]['high'].rolling(window=self.window).max() + self.data[symbol]['low'].rolling(window=self.window).min() + 2 * self.data[symbol]['close'].rolling(window=self.window).mean()) / 4
            self.data[symbol + '_KC_upper'] = (self.data[symbol]['high'].rolling(window=self.window).max() - self.data[symbol]['low'].rolling(window=self.window).min()) / 2
            self.data[symbol + '_KC_lower'] = (self.data[symbol]['low'].rolling(window=self.window).min() - self.data[symbol]['high'].rolling(window=self.window).max()) / 2

def get_donchian_channel(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_DC_upper'] = self.data[symbol]['high'].rolling(window=self.window).max()
            self.data[symbol + '_DC_lower'] = self.data[symbol]['low'].rolling(window=self.window).min()

def get_ease_of_movement(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_EMV'] = (self.data[symbol]['high'].diff(1) + self.data[symbol]['low'].diff(1)) * (self.data[symbol]['high'] - self.data[symbol]['low']) / (2 * self.data[symbol]['volume'])
            self.data[symbol + '_EMV'] = self.data[symbol + '_EMV'].rolling(window=self.window).mean()

def get_force_index(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_FI'] = self.data[symbol]['close'].diff(1) * self.data[symbol]['volume']
            self.data[symbol + '_FI'] = self.data[symbol + '_FI'].rolling(window=self.window).mean()

def get_know_sure_thing(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            ROC_1 = self.data[symbol]['close'].diff(10)
            ROC_2 = self.data[symbol]['close'].diff(15)
            ROC_3 = self.data[symbol]['close'].diff(20)
            ROC_4 = self.data[symbol]['close'].diff(30)
            self.data[symbol + '_KST'] = (ROC_1.rolling(window=self.window).sum() + ROC_2.rolling(window=self.window).sum() * 2 + ROC_3.rolling(window=self.window).sum() * 3 + ROC_4.rolling(window=self.window).sum() * 4) / 6
            self.data[symbol + '_signal'] = self.data[symbol + '_KST'].rolling(window=9).mean()

def get_true_strength_index(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_M'] = self.data[symbol]['close'].diff(1)
            self.data[symbol + '_M'] = self.data[symbol + '_M'].rolling(window=self.window).mean()
            self.data[symbol + '_A'] = self.data[symbol + '_M'].diff(1)
            self.data[symbol + '_A'] = self.data[symbol + '_A'].rolling(window=self.window).mean()
            self.data[symbol + '_TSI'] = 100 * self.data[symbol + '_M'] / self.data[symbol + '_A']

def get_chande_momentum_oscillator(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_CMO'] = (self.data[symbol]['close'] - self.data[symbol]['close'].rolling(window=self.window).mean()) / (self.data[symbol]['close'] + self.data[symbol]['close'].rolling(window=self.window).mean())

def get_ultimate_oscillator(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_BP'] = self.data[symbol]['close'] - self.data[symbol]['low'].rolling(window=self.window).min()
            self.data[symbol + '_TR'] = self.data[symbol]['high'].rolling(window=self.window).max() - self.data[symbol]['low'].rolling(window=self.window).min()
            self.data[symbol + '_UO'] = 100 * ((4 * self.data[symbol + '_BP'].rolling(window=self.window).sum()) / self.data[symbol + '_TR'].rolling(window=self.window).sum() + (2 * self.data[symbol + '_BP'].rolling(window=self.window).sum()) / self.data[symbol + '_TR'].rolling(window=self.window).sum() + (self.data[symbol + '_BP'].rolling(window=self.window).sum()) / self.data[symbol + '_TR'].rolling(window=self.window).sum())

def get_vwap(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_VWAP'] = (self.data[symbol]['volume'] * (self.data[symbol]['high'] + self.data[symbol]['low'] + self.data[symbol]['close']) / 3).cumsum() / self.data[symbol]['volume'].cumsum()

def get_price_volume_trend(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_PVT'] = self.data[symbol]['volume'] * (self.data[symbol]['close'] - self.data[symbol]['close'].shift(1)) / self.data[symbol]['close'].shift(1)
            self.data[symbol + '_PVT'] = self.data[symbol + '_PVT'].cumsum()
    
def get_negative_volume_index(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_NVI'] = 1000
            for i in range(1, len(self.data[symbol])) :
                if self.data[symbol]['volume'][i] < self.data[symbol]['volume'][i - 1] :
                    self.data[symbol + '_NVI'][i] = self.data[symbol + '_NVI'][i - 1] + (self.data[symbol]['close'][i] - self.data[symbol]['close'][i - 1]) / self.data[symbol]['close'][i - 1] * self.data[symbol + '_NVI'][i - 1]
                else :
                    self.data[symbol + '_NVI'][i] = self.data[symbol + '_NVI'][i - 1]

def get_positive_volume_index(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_PVI'] = 1000
            for i in range(1, len(self.data[symbol])) :
                if self.data[symbol]['volume'][i] > self.data[symbol]['volume'][i - 1] :
                    self.data[symbol + '_PVI'][i] = self.data[symbol + '_PVI'][i - 1] + (self.data[symbol]['close'][i] - self.data[symbol]['close'][i - 1]) / self.data[symbol]['close'][i - 1] * self.data[symbol + '_PVI'][i - 1]
                else :
                    self.data[symbol + '_PVI'][i] = self.data[symbol + '_PVI'][i - 1]
    
def get_accumulation_distribution(self) :
    if self.check_symbol_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_AD'] = (self.data[symbol]['high'] - self.data[symbol]['close'].shift(1)) / (self.data[symbol]['high'] - self.data[symbol]['low']) * self.data[symbol]['volume'] + self.data[symbol + '_AD'].shift(1)

def get_chaikin_money_flow(self) :
    if self.check_symbol_defined() & self._check_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_CMF'] = ((self.data[symbol]['close'] - self.data[symbol]['low']) - (self.data[symbol]['high'] - self.data[symbol]['close'])) / (self.data[symbol]['high'] - self.data[symbol]['low'])
            self.data[symbol + '_CMF'] = self.data[symbol + '_CMF'].rolling(window=self.window).mean()

def get_stochastic_rsi(self) :
    if self._chck_symbol_defined() & self._chck_window_defined() :
        for symbol in self.symbols :
            delta = self.data[symbol].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
            RS = gain / loss
            RSI = 100 - (100 / (1 + RS))
            self.data[symbol + '_RSI' + str(self.window)] = RSI
            self.data[symbol + '_K'] = (RSI - RSI.rolling(window=self.window).min()) / (RSI.rolling(window=self.window).max() - RSI.rolling(window=self.window).min())

def get_average_directional_index(self) :
    if self._chck_symbol_defined() & self._chck_window_defined() :
        for symbol in self.symbols :
            delta = self.data[symbol].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=self.window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=self.window).mean()
            RS = gain / loss
            RSI = 100 - (100 / (1 + RS))
            self.data[symbol + '_RSI' + str(self.window)] = RSI
            self.data[symbol + '_ADX'] = (self.data[symbol + '_RSI' + str(self.window)].diff(1).abs() / self.data[symbol + '_RSI' + str(self.window)].diff(1).abs().rolling(window=self.window).sum()) * 100
    
def get_aroon_oscillator(self) :
    if self._chck_symbol_defined() & self._chck_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_up_' + str(self.window)] = self.data[symbol]['high'].rolling(window=self.window).apply(lambda x: x.argmax())
            self.data[symbol + '_down_' + str(self.window)] = self.data[symbol]['low'].rolling(window=self.window).apply(lambda x: x.argmin())
            self.data[symbol + '_Aroon_up'] = 100 * (self.window - self.data[symbol + '_up_' + str(self.window)]) / self.window
            self.data[symbol + '_Aroon_down'] = 100 * (self.window - self.data[symbol + '_down_' + str(self.window)]) / self.window
            self.data[symbol + '_Aroon_oscillator'] = self.data[symbol + '_Aroon_up'] - self.data[symbol + '_Aroon_down']

def get_aligator(self) :
    if self._chck_symbol_defined() & self._chck_window_defined() :
        for symbol in self.symbols :
            self.data[symbol + '_jaw'] = self.data[symbol]['high'].rolling(window=self.window).max()
            self.data[symbol + '_teeth'] = self.data[symbol]['low'].rolling(window=self.window).min()
            self.data[symbol + '_lips'] = (self.data[symbol + '_jaw'] + self.data[symbol + '_teeth']) / 2

def get_fractals(self) :
    if self._chck_symbol_defined()  :
        for symbol in self.symbols :
            self.data[symbol + '_up'] = self.data[symbol]['high'].rolling(window=3).apply(lambda x: x.argmax())
            self.data[symbol + '_down'] = self.data[symbol]['low'].rolling(window=3).apply(lambda x: x.argmin())

def get_awesome_oscillator(self) :
    if self._chck_symbol_defined()  :
        for symbol in self.symbols :
            self.data[symbol + '_AO'] = (self.data[symbol]['high'].rolling(window=5).mean() + self.data[symbol]['low'].rolling(window=5).mean()) / 2 - (self.data[symbol]['high'].rolling(window=34).mean() + self.data[symbol]['low'].rolling(window=34).mean()) / 2
    


def indicators():
    return  [   "sma",
                "rsi",
                "macd",
                "std",
                "bollinger_bands",
                "ema"
            ]
                # "adx",
                # "atr",
                # "stochastic_oscillator",
                # "momentum",
                # "williams_r",
                # "cci",
                # "aroon",
                # "obv",
                # "mfi",
                # "pivot_points",
                # "fibonacci_retracement",
                # "trix",
                # "vortex",
                # "kst",
                # "ichimoku_cloud",
                # "fisher_transform",
                # "chaikin_oscillator",
                # "parabolic_sar",
                # "keltner_channel",
                # "donchian_channel",
                # "ease_of_movement",
                # "force_index",
                # "know_sure_thing",
                # "true_strength_index",
                # "chande_momentum_oscillator",
                # "ultimate_oscillator",
                # "vwap",
                # "price_volume_trend",
                # "negative_volume_index",
                # "positive_volume_index",
                # "accumulation_distribution",
                # "chaikin_money_flow",
                # "stochastic_rsi",
                # "trix",
                # "average_directional_index",
                # "aroon_oscillator",
                # "aligator",
                # "fractals",
                # "awesome_oscillator"
                # ]

def calculate_indicator(indicator, prices, col, window=None, short_window=None, long_window=None, span=None, smoothing=None) :
    # create task for all indicators
    if indicator == "sma" :
        return get_sma(indicator, prices, col, window)
    elif indicator == "rsi" :
        return get_rsi(indicator, prices, col, window)
    elif indicator == "macd" :
        return get_macd(indicator, prices, col, short_window, long_window, span)
    elif indicator == "std" :
        return get_std(indicator, prices, col, window)
    elif indicator == "bollinger_bands" :
        return get_bollinger_bands(indicator, prices, col, window)
    elif indicator == "ema" :
        return get_ema(indicator, prices, col, window)
    elif indicator == "adx" :
        return get_adx()
    elif indicator == "atr" :
        get_atr()
    elif indicator == "stochastic_oscillator" :
        get_stochastic_oscillator()
    elif indicator == "momentum" :
        get_momentum()
    elif indicator == "williams_r" :
        get_williams_r()
    elif indicator == "cci" :
        get_cci()
    elif indicator == "aroon" :
        get_aroon()
    elif indicator == "obv" :
        get_obv()
    elif indicator == "mfi" :
        get_mfi()
    elif indicator == "pivot_points" :
        get_pivot_points()
    elif indicator == "fibonacci_retracement" :
        get_fibonacci_retracement()
    elif indicator == "trix" :
        get_trix()
    elif indicator == "vortex" :
        get_vortex()
    elif indicator == "kst" :
        get_kst()
    elif indicator == "ichimoku_cloud" :
        get_ichimoku_cloud()
    elif indicator == "fisher_transform" :
        get_fisher_transform()
    elif indicator == "chaikin_oscillator" :
        get_chaikin_oscillator()
    elif indicator == "parabolic_sar" :
        get_parabolic_sar()
    elif indicator == "keltner_channel" :
        get_keltner_channel()
    elif indicator == "donchian_channel" :
        get_donchian_channel()
    elif indicator == "ease_of_movement" :
        get_ease_of_movement()
    elif indicator == "force_index" :
        get_force_index()
    elif indicator == "know_sure_thing" :
        get_know_sure_thing()
    elif indicator == "true_strength_index" :
        get_true_strength_index()
    elif indicator == "chande_momentum_oscillator" :
        get_chande_momentum_oscillator()
    elif indicator == "ultimate_oscillator" :
        get_ultimate_oscillator()
    elif indicator == "vwap" :
        get_vwap()
    elif indicator == "price_volume_trend" :
        get_price_volume_trend()
    elif indicator == "negative_volume_index" :
        get_negative_volume_index()
    elif indicator == "positive_volume_index" :
        get_positive_volume_index()
    elif indicator == "accumulation_distribution" :
        get_accumulation_distribution()
    elif indicator == "chaikin_money_flow" :
        get_chaikin_money_flow()
    elif indicator == "stochastic_rsi" :
        get_stochastic_rsi()
    elif indicator == "average_directional_index" :
        get_average_directional_index()
    elif indicator == "aroon_oscillator" :
        get_aroon_oscillator()
    elif indicator == "aligator" :
        get_aligator()
    elif indicator == "fractals" :
        get_fractals()
    elif indicator == "awesome_oscillator" :
        get_awesome_oscillator()