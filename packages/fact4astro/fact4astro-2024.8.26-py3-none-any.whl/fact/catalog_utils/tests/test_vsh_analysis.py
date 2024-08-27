import unittest
import numpy as np
from astropy.table import Table
from fact.catalog_utils.vsh_analysis import (
    vsh_fit,
    vsh_fit_4_table,
    init_par_names,
    print_vsh_result,
    print_vsh_result_4_dict,
    save_vsh_result,
    write_textable
)


class TestVSHAnalysis(unittest.TestCase):

    def setUp(self):
        """Set up test data."""
        self.ra = np.linspace(0, 2 * np.pi, 10)
        self.dec = np.linspace(-np.pi/2, np.pi/2, 10)
        self.dra = np.random.normal(0, 0.1, 10)
        self.ddec = np.random.normal(0, 0.1, 10)
        self.e_dra = np.full(10, 0.1)
        self.e_ddec = np.full(10, 0.1)
        self.cov = None

        self.data_tab = Table({
            'dra': self.dra,
            'ddec': self.ddec,
            'ra': np.rad2deg(self.ra),
            'dec': np.rad2deg(self.dec),
            'dra_err': self.e_dra,
            'ddec_err': self.e_ddec
        })

    def test_vsh_fit(self):
        """Test the vsh_fit function."""
        params, sigs, corr_mat = vsh_fit(
            self.dra, self.ddec, self.e_dra, self.e_ddec,
            self.ra, self.dec, self.cov, fit_type="full", l_max=1
        )
        self.assertEqual(len(params), 6)
        self.assertEqual(len(sigs), 6)
        self.assertEqual(corr_mat.shape, (6, 6))

    def test_vsh_fit_4_table(self):
        """Test the vsh_fit_4_table function."""
        output = vsh_fit_4_table(
            self.data_tab, fit_type="full", return_aux=False, l_max=1)
        self.assertIn("pmt", output)
        self.assertIn("sig", output)
        self.assertIn("cor_mat", output)
        self.assertEqual(len(output["pmt"]), 6)

    def test_init_par_names(self):
        """Test the init_par_names function."""
        par_names = init_par_names(6)
        self.assertEqual(len(par_names), 6)
        self.assertEqual(par_names[0], "D1")

        par_names_16 = init_par_names(16)
        self.assertEqual(len(par_names_16), 16)
        self.assertEqual(par_names_16[-1], "M20")

    def test_print_vsh_result(self):
        """Test the print_vsh_result function."""
        params = np.random.random(6)
        sigs = np.random.random(6) * 0.1
        corr_mat = np.eye(6)
        try:
            print_vsh_result(params, sigs, corr_mat)
        except Exception as e:
            self.fail(f"print_vsh_result failed with error: {e}")

    def test_print_vsh_result_4_dict(self):
        """Test the print_vsh_result_4_dict function."""
        output = {
            "pmt": np.random.random(6),
            "sig": np.random.random(6) * 0.1,
            "cor_mat": np.eye(6)
        }
        try:
            print_vsh_result_4_dict(output)
        except Exception as e:
            self.fail(f"print_vsh_result_4_dict failed with error: {e}")

    def test_save_vsh_result(self):
        """Test the save_vsh_result function."""
        params = np.random.random(6)
        sigs = np.random.random(6) * 0.1
        try:
            save_vsh_result(params, sigs, "test_output.txt")
        except Exception as e:
            self.fail(f"save_vsh_result failed with error: {e}")

    def test_write_textable(self):
        """Test the write_textable function."""
        cat_names = ["Catalog1", "Catalog2"]
        pmts = [np.random.random(6) for _ in range(2)]
        sigs = [np.random.random(6) * 0.1 for _ in range(2)]
        try:
            write_textable(cat_names, pmts, sigs, par_names=None)
        except Exception as e:
            self.fail(f"write_textable failed with error: {e}")


if __name__ == "__main__":
    unittest.main()
