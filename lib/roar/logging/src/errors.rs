// -- https://github.com/StormWorld0/storm-framework
// -- SMF License
use pyo3::prelude::*;
use pyo3::exceptions::{PyTypeError, PyValueError, PyOSError};
use std::fmt;

#[derive(Debug)]
pub enum PrintError {
    TypeError(String),
    ValueError(String),
    IOError(std::io::Error), // Gunakan tipe asli std::io
    PythonError(PyErr),
}

impl fmt::Display for PrintError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            PrintError::TypeError(msg) => write!(f, "Type Error: {}", msg),
            PrintError::ValueError(msg) => write!(f, "Value Error: {}", msg),
            PrintError::IOError(err) => write!(f, "I/O System Error: {}", err),
            PrintError::PythonError(err) => write!(f, "Python Internal Error: {}", err),
        }
    }
}

impl std::error::Error for PrintError {
    // Memberikan akses ke root cause error jika diperlukan oleh debugger
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            PrintError::IOError(err) => Some(err),
            _ => None,
        }
    }
}

// Implementasi konversi otomatis dari std::io::Error
impl From<std::io::Error> for PrintError {
    fn from(err: std::io::Error) -> Self {
        PrintError::IOError(err)
    }
}

// Implementasi konversi otomatis dari PyErr (untuk PyO3)
impl From<PyErr> for PrintError {
    fn from(err: PyErr) -> Self {
        PrintError::PythonError(err)
    }
}

// Bagian Krusial: Konversi balik ke Python Exception
impl From<PrintError> for PyErr {
    fn from(err: PrintError) -> PyErr {
        match err {
            PrintError::TypeError(msg) => PyTypeError::new_err(msg),
            PrintError::ValueError(msg) => PyValueError::new_err(msg),
            // Mengonversi std::io::Error langsung ke PyOSError yang akurat
            PrintError::IOError(err) => PyOSError::new_err(err.to_string()),
            PrintError::PythonError(err) => err,
        }
    }
}

pub type PrintResult<T> = Result<T, PrintError>;

