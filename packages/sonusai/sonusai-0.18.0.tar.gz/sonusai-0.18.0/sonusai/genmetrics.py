# Generate mixdb metrics based on metrics listed in config.yml


class MixtureMetrics:
    @property
    def mxsnr(self):
        ...

    @property
    def mxssnravg(self):
        ...

    @property
    def mxssnrstd(self):
        ...

    @property
    def mxssnrdavg(self):
        ...

    @property
    def mxssnrdstd(self):
        ...

    @property
    def mxpesq(self):
        ...

    @property
    def mxwsdr(self):
        ...

    @property
    def mxpd(self):
        ...

    @property
    def mxstoi(self):
        ...

    @property
    def mxcsig(self):
        ...

    @property
    def mxcbak(self):
        ...

    @property
    def mxcovl(self):
        ...

    def mxwer(self, engine: str, model: str):
        ...

    @property
    def tdco(self):
        ...

    @property
    def tmin(self):
        ...

    @property
    def tmax(self):
        ...

    @property
    def tpkdb(self):
        ...

    @property
    def tlrms(self):
        ...

    @property
    def tpkr(self):
        ...

    @property
    def ttr(self):
        ...

    @property
    def tcr(self):
        ...

    @property
    def tfl(self):
        ...

    @property
    def tpkc(self):
        ...

    @property
    def ndco(self):
        ...

    @property
    def nmin(self):
        ...

    @property
    def nmax(self):
        ...

    @property
    def npkdb(self):
        ...

    @property
    def nlrms(self):
        ...

    @property
    def npkr(self):
        ...

    @property
    def ntr(self):
        ...

    @property
    def ncr(self):
        ...

    @property
    def nfl(self):
        ...

    @property
    def npkc(self):
        ...

    @property
    def sedavg(self):
        ...

    @property
    def sedcnt(self):
        ...

    @property
    def sedtopn(self):
        ...
