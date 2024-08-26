from ...interface import IPacker


class InstrumentDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return [str(self._obj.RID), str(self._obj.InstrumentID), str(self._obj.ExchangeID), str(self._obj.InstrumentName),
                str(self._obj.UniCode), str(self._obj.ProductID), int(self._obj.ProductType), str(self._obj.DeliveryYear),
                str(self._obj.DeliveryMonth), str(self._obj.CreateDate), str(self._obj.OpenDate), str(self._obj.ExpireDate),
                str(self._obj.StartDelivDate), str(self._obj.EndDelivDate), int(self._obj.MaxMarketOrderVolume), int(self._obj.MinMarketOrderVolume),
                int(self._obj.MaxLimitOrderVolume), int(self._obj.MinLimitOrderVolume), int(self._obj.VolumeMultiple), float(self._obj.PriceTick),
                int(self._obj.PricePrecision), bool(self._obj.IsTrading), bool(self._obj.MaxMarginSideAlgorithm), str(self._obj.ProductGroupID),
                float(self._obj.StrikePrice), int(self._obj.OptionsType), str(self._obj.UnderlyingInstrID), float(self._obj.UnderlyingMultiple),
                int(self._obj.CombinationType), int(self._obj.StrikeModeType), float(self._obj.ObjectPrice), float(self._obj.ObjectMarginRatioByMoney),
                float(self._obj.ObjectMarginRatioByVolume), float(self._obj.EnsureRatio1), float(self._obj.EnsureRatio2), bool(self._obj.IsCloseToday)]

    def tuple_to_obj(self, t):
        if len(t) >= 36:
            self._obj.RID = t[0]
            self._obj.InstrumentID = t[1]
            self._obj.ExchangeID = t[2]
            self._obj.InstrumentName = t[3]
            self._obj.UniCode = t[4]
            self._obj.ProductID = t[5]
            self._obj.ProductType = t[6]
            self._obj.DeliveryYear = t[7]
            self._obj.DeliveryMonth = t[8]
            self._obj.CreateDate = t[9]
            self._obj.OpenDate = t[10]
            self._obj.ExpireDate = t[11]
            self._obj.StartDelivDate = t[12]
            self._obj.EndDelivDate = t[13]
            self._obj.MaxMarketOrderVolume = t[14]
            self._obj.MinMarketOrderVolume = t[15]
            self._obj.MaxLimitOrderVolume = t[16]
            self._obj.MinLimitOrderVolume = t[17]
            self._obj.VolumeMultiple = t[18]
            self._obj.PriceTick = t[19]
            self._obj.PricePrecision = t[20]
            self._obj.IsTrading = t[21]
            self._obj.MaxMarginSideAlgorithm = t[22]
            self._obj.ProductGroupID = t[23]
            self._obj.StrikePrice = t[24]
            self._obj.OptionsType = t[25]
            self._obj.UnderlyingInstrID = t[26]
            self._obj.UnderlyingMultiple = t[27]
            self._obj.CombinationType = t[28]
            self._obj.StrikeModeType = t[29]
            self._obj.ObjectPrice = t[30]
            self._obj.ObjectMarginRatioByMoney = t[31]
            self._obj.ObjectMarginRatioByVolume = t[32]
            self._obj.EnsureRatio1 = t[33]
            self._obj.EnsureRatio2 = t[34]
            self._obj.IsCloseToday = t[35]

            return True
        return False
