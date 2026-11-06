"""Pruebas de fenomenología del reactor CSTR (hmi/cstr_model.py). Se corren con:  python -m unittest discover tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "hmi"))
import cstr_model as m  # noqa: E402


def estacionario(u, s=None, minutos=600):
    s = m.integrate(s or m.State(), u, minutos)
    return s, m.derivatives(s, u)


class CSTR(unittest.TestCase):
    def test_caso_base_es_estado_estacionario_exacto(self):
        s, d = estacionario(m.Inputs())
        self.assertAlmostEqual(s.T, 310.0, places=3)
        self.assertAlmostEqual(m.conversion(s), 0.15, places=4)
        self.assertLess(abs(d["T"]), 1e-6)

    def test_caso_base_termicamente_estable(self):
        # La remoción de calor crece con T más rápido que la generación (criterio de van Heerden)
        u, h = m.Inputs(), 0.01
        ca = lambda T: m.CA_IN * u.F / m.V / (u.F / m.V + m.rate_constant(T))
        qg = lambda T: m.rate_constant(T) * ca(T) * (-m.DH) * m.V
        def qr(T):
            tj = (u.Fj * m.RHO * m.CP * u.Tjin + u.UA * T) / (u.Fj * m.RHO * m.CP + u.UA)
            return u.UA * (T - tj) + u.F * m.RHO * m.CP * (T - u.Tin)
        self.assertGreater((qr(310 + h) - qr(310 - h)) / (2 * h), (qg(310 + h) - qg(310 - h)) / (2 * h))

    def test_falla_del_precalentador_dispara_el_reactor(self):
        s, _ = estacionario(m.Inputs(dTin=5))
        self.assertAlmostEqual(s.T, 339.1, delta=0.5)
        self.assertEqual(m.alarm_level(s.T), 2)

    def test_el_operador_recupera_el_reactor(self):
        s, _ = estacionario(m.Inputs(dTin=5))
        s, _ = estacionario(m.Inputs(dTin=5, Fj=40, Tjin=285), s)
        self.assertAlmostEqual(s.T, 315.8, delta=0.5)
        self.assertEqual(m.alarm_level(s.T), 0)

    def test_mas_agitacion_mejora_la_transferencia(self):
        self.assertGreater(m.Inputs(N=250).UA, m.Inputs(N=150).UA)
        self.assertLess(m.Inputs(fouling=0.8).UA, m.Inputs().UA)


if __name__ == "__main__":
    unittest.main()
