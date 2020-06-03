import random as rand 
import math

class NoiseParameters():
    def __init__(self, octaves, amplitude, smoothness, roughness, heightOffset):
        self.octaves = octaves
        self.amplitude = amplitude
        self.smoothness = smoothness
        self.roughness = roughness
        self.heightOffset = heightOffset

class NoiseGen():
    def __init__(self, seed):
        self.seed = seed
        self.noiseParams = NoiseParameters(
            7, 50, 400, 0.3, 20
        )

    def _getNoise2(self, n):
        n += self.seed 
        n = (int(n) << 13) ^ int(n)
        newn = (n * (n * n * 60493 + 19990303) + 1376312589) & 0x7fffffff
        newn_2 = (n * (n * n * 12345 + 99999999) + 1234567890) & 0x7fffffff
        newn_3 = (n + (n + n + 12345 * 99999999) * 1234567890) & 0x7fffffff
        return (1.0 - (float(newn) / 1073741824.0)) * (1.0 - (float(newn_2) / 1073741824.0)) + (1.0 - (float(newn_3) / 1073741824.0)) 

    def _getNoise(self, x, z):
        return self._getNoise2(x + z * 5)

    def _lerp(self, a, b, z):
        mu2 = (1.0 - math.cos(z * 3.14)) / 2.0
        return (a * (1 - mu2) + b * mu2)

    def _noise(self, x, z):
        floorX = float(int(x))
        floorZ = float(int(z))

        s = 0.0,
        t = 0.0,
        u = 0.0,
        v = 0.0;#Integer declaration

        s = self._getNoise(floorX,      floorZ)
        t = self._getNoise(floorX + 1,  floorZ)
        u = self._getNoise(floorX,      floorZ + 1)
        v = self._getNoise(floorX + 1,  floorZ + 1)

        rec1 = self._lerp(s, t, x - floorX)
        rec2 = self._lerp(u, v, x - floorX)
        rec3 = self._lerp(rec1, rec2, z - floorZ)
        return rec3

    def getHeight(self, x, z):
        totalValue = 0.0

        for a in range(self.noiseParams.octaves - 1):
            freq = math.pow(2.0, a)
            amp  = math.pow(self.noiseParams.roughness, a)
            totalValue += self._noise(
                (float(x)) * freq / self.noiseParams.smoothness,
                (float(z)) * freq / self.noiseParams.smoothness
            ) * self.noiseParams.amplitude

        result = (((totalValue / 2.1) + 1.2) * self.noiseParams.amplitude) + self.noiseParams.heightOffset

        return (totalValue / 5) + self.noiseParams.heightOffset
        #return result

class NoiseGen_3d():
    def __init__(self, seed):
        self.seed = seed
        self.noiseParams_3d = NoiseParameters(
            5, 100, 100, 0.3, 10
        )

    def _getNoise2_3d(self, n):
        n *= self.seed 
        n = (int(n) << 13)# ^ int(n)
        newn = (n * (n * n * 60493 + 19990303) + 1376312589) & 0x7fffffff
        newn_2 = (n * (n * n * 12345 + 99999999) + 1234567890) & 0x7fffffff
        #newn_3 = (n // (n // n // 60493 - 19990303) - 1376312589) & 0x7fffffff
        return (1.0 - (float(newn) / 1073741824.0))# - (1.0 - (float(newn_2) / 1073741824.0)) 

    def _getNoise_3d(self, x, z, y):
        return self._getNoise2_3d(x + z + y)

    def _lerp(self, a, b, z):
        mu2 = (1.0 - math.cos(z * 3.14)) / 2.0
        return (a * (1 - mu2) + b * mu2)

    def _noise_3d(self, x, z, y):
        floorX = float(int(x))
        floorZ = float(int(z))
        floorY = float(int(y))

        e = 0.0,
        f = 0.0,
        g = 0.0,
        h = 0.0,
        i = 0.0,
        j = 0.0,
        k = 0.0,
        l = 0.0;#Integer declaration

        e = self._getNoise_3d(floorX,      floorZ,      floorY)

        f = self._getNoise_3d(floorX + 1,  floorZ,      floorY)
        g = self._getNoise_3d(floorX,      floorZ + 1,  floorY)
        h = self._getNoise_3d(floorX,      floorZ,      floorY + 1)

        i = self._getNoise_3d(floorX + 1,  floorZ + 1,  floorY)
        j = self._getNoise_3d(floorX,      floorZ + 1,  floorY + 1)
        l = self._getNoise_3d(floorX + 1,   floorZ,     floorY + 1)

        k = self._getNoise_3d(floorX + 1,  floorZ + 1,  floorY + 1)

        rec1 = self._lerp(e, f, x - floorX)
        rec2 = self._lerp(g, h, x - floorX)
        rec3 = self._lerp(i, j, x - floorX)
        rec4 = self._lerp(l, k, x - floorX)
        rec5 = self._lerp(rec1, rec2, z - floorZ)
        rec6 = self._lerp(rec3, rec4, z - floorZ)
        rec7 = self._lerp(rec5, rec6, z - floorZ)
        return rec7

    def getHeight_3d(self, x, z, y):
        totalValue = 0.0

        for a in range(self.noiseParams_3d.octaves - 1):
            freq = math.pow(2.0, a)
            amp  = math.pow(self.noiseParams_3d.roughness, a)
            totalValue += self._noise_3d(
                (float(x)) * freq / self.noiseParams_3d.smoothness,
                (float(z)) * freq / self.noiseParams_3d.smoothness,
                (float(y)) * freq / self.noiseParams_3d.smoothness
            ) * self.noiseParams_3d.amplitude

        result = (((totalValue / 2.1) + 1.2) * self.noiseParams_3d.amplitude) + self.noiseParams_3d.heightOffset

        return (totalValue / 5) + self.noiseParams_3d.heightOffset
        #return result

class NoiseGen_2():
    def __init__(self, seed):
        self.seed_2 = seed
        self.noiseParams_2 = NoiseParameters(
            7, 50, 250, 0.3, 20
        )

    def _getNoise2_2(self, n):
        n += self.seed_2
        n = (int(n) << 13) ^ int(n)
        newn = (n * (n * n * 84923 + 924617832) + 3364853721) & 0x7fffffff
        #newn = (n * (n * n * 60493 + 19990303) + 1376312589) & 0x7fffffff
        newn_2 = (n * (n * n * 12345 + 99999999) + 1234567890) & 0x7fffffff
        newn_3 = (n + (n + n + 12345 * 99999999) * 1234567890) & 0x7fffffff
        return (1.0 - (float(newn) / 1073741824.0)) 

    def _getNoise_2(self, x, z):
        return self._getNoise2_2(x + z * 5)

    def _lerp_2(self, a, b, z):
        mu2 = (1.0 - math.cos(z * 3.14)) / 2.0
        return (a * (1 - mu2) + b * mu2)

    def _noise_2(self, x, z):
        floorX = float(int(x))
        floorZ = float(int(z))

        s = 0.0,
        t = 0.0,
        u = 0.0,
        v = 0.0;#Integer declaration

        s = self._getNoise_2(floorX,      floorZ)
        t = self._getNoise_2(floorX + 1,  floorZ)
        u = self._getNoise_2(floorX,      floorZ + 1)
        v = self._getNoise_2(floorX + 1,  floorZ + 1)

        rec1 = self._lerp_2(s, t, x - floorX)
        rec2 = self._lerp_2(u, v, x - floorX)
        rec3 = self._lerp_2(rec1, rec2, z - floorZ)
        return rec3

    def getHeight_2(self, x, z):
        totalValue = 0.0

        for a in range(self.noiseParams_2.octaves - 1):
            freq = math.pow(2.0, a)
            amp  = math.pow(self.noiseParams_2.roughness, a)
            totalValue += self._noise_2(
                (float(x)) * freq / self.noiseParams_2.smoothness,
                (float(z)) * freq / self.noiseParams_2.smoothness
            ) * self.noiseParams_2.amplitude

        result = (((totalValue / 2.1) + 1.2) * self.noiseParams_2.amplitude) + self.noiseParams_2.heightOffset

        return (totalValue / 5) + self.noiseParams_2.heightOffset
        #return result

