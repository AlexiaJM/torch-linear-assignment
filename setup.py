import os
import setuptools
import torch
import torch.utils.cpp_extension as torch_cpp_ext

def get_build_ext_modules():
    compile_args_cxx = ["-O3"]
    compile_args_nvcc = []

    # Try to match PyTorch's C++ ABI
    try:
        if torch._C._GLIBCXX_USE_CXX11_ABI:
            print("PyTorch built with C++11 ABI")
            # You might not need to explicitly add this if your compiler defaults to C++11 ABI
            # compile_args_cxx.append("-D_GLIBCXX_USE_CXX11_ABI=1")
            # compile_args_nvcc.append("-D_GLIBCXX_USE_CXX11_ABI=1") # Add for nvcc if needed
        else:
            print("PyTorch built with old C++ ABI")
            compile_args_cxx.append("-D_GLIBCXX_USE_CXX11_ABI=0")
            compile_args_nvcc.append("-D_GLIBCXX_USE_CXX11_ABI=0") # Add for nvcc
    except AttributeError:
        print("Could not determine PyTorch C++ ABI. Proceeding without explicit ABI flag.")
        # Fallback or manual inspection needed if this fails


    if torch.backends.cuda.is_built() and int(os.environ.get("TLA_BUILD_CUDA", "1")) and torch.cuda.is_available():
        compile_args = {"cxx": compile_args_cxx}
        if os.environ.get("CC", None) is not None:
            compile_args["nvcc"] = ["-ccbin", os.environ["CC"]] + compile_args_nvcc
        else:
             compile_args["nvcc"] = compile_args_nvcc # Ensure nvcc also gets ABI flag if needed

        return [
            torch_cpp_ext.CUDAExtension(
                "torch_linear_assignment._backend",
                [
                    "src/torch_linear_assignment_cuda.cpp",
                    "src/torch_linear_assignment_cuda_kernel.cu"
                ],
                extra_compile_args=compile_args
            )
        ]
    return [
        torch_cpp_ext.CppExtension(
            "torch_linear_assignment._backend",
            [
                "src/torch_linear_assignment.cpp",
            ],
            extra_compile_args={"cxx": compile_args_cxx}
        )
    ]

with open("requirements.txt", "r") as fp:
    required_packages = [line.strip() for line in fp.readlines()]


def get_build_ext():
    import torch.utils.cpp_extension as torch_cpp_ext

    return torch_cpp_ext.BuildExtension


with open("README.md") as fp:
    long_description = fp.read()


if __name__ == '__main__':
    setuptools.setup(
        name="torch-linear-assignment",
        version="0.0.3",
        author="Ivan Karpukhin",
        author_email="karpuhini@yandex.ru",
        description="Batched linear assignment with PyTorch and CUDA.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        packages=["torch_linear_assignment"],
        ext_modules=get_build_ext_modules(),
        install_requires=required_packages,
        cmdclass={
            "build_ext": get_build_ext()
        }
    )
