import pytest
import numpy as np

from tme.package import GaussianKernel, KernelFitting
from tme.analyzer import PeakCallerFast

class TestKernelFitting:
    def setup_method(self):
        self.number_of_peaks = 100
        self.min_distance = 5
        self.data = np.random.rand(100, 100, 100)
        self.rotation_matrix = np.eye(3)

        self.kernel_box = np.random.choice(np.arange(5, 15), size=self.data.ndim)
        self.template = np.random.rand(*self.kernel_box)

    @pytest.mark.parametrize(
        "kernel",
        [
            (GaussianKernel),
        ],
    )
    def test_initialization(self, kernel):
        kernel_params = kernel.estimate_parameters(self.template)
        _ = KernelFitting(
            number_of_peaks=self.number_of_peaks,
            min_distance=self.min_distance,
            kernel_box=self.kernel_box,
            kernel_class=kernel,
            kernel_params=kernel_params,
            peak_caller=PeakCallerFast,
        )

    @pytest.mark.parametrize("kernel",[GaussianKernel])
    def test__call__(self, kernel):
        kernel_params = kernel.estimate_parameters(self.template)
        score_analyzer = KernelFitting(
            number_of_peaks=self.number_of_peaks,
            min_distance=self.min_distance,
            kernel_box=self.kernel_box,
            kernel_class=kernel,
            kernel_params=kernel_params,
            peak_caller=PeakCallerFast,
        )
        score_analyzer(self.data, rotation_matrix=self.rotation_matrix)


class TestKernel:
    def setup_method(self):
        self.number_of_peaks = 100
        self.min_distance = 5
        self.data = np.random.rand(100, 100, 100)
        self.rotation_matrix = np.eye(3)

    def test_initialization(self):
        _ = GaussianKernel()

    @pytest.mark.parametrize(
        "kernel",
        [
            GaussianKernel,
        ],
    )
    def test_fit(self, kernel):
        params, success, final_error = kernel.fit(self.data)
        assert isinstance(params, tuple)
        assert len(params) == 3

    @pytest.mark.parametrize(
        "kernel",
        [
            GaussianKernel,
        ],
    )
    def test_fit_height(self, kernel):
        params, success, final_error = kernel.fit(self.data)
        height, mean, cov = params
        params, succes, final_error = kernel.fit_height(
            data=self.data, mean=mean, cov=cov
        )
        assert np.allclose(params[1], mean)
        assert np.allclose(params[2], cov)

    @pytest.mark.parametrize(
        "kernel",
        [
            GaussianKernel,
        ],
    )
    def test_score(self, kernel):
        params, *_ = kernel.fit(self.data)
        params2, *_ = kernel.fit(self.data)

        score = kernel.score(params, params2)
        assert score == 1