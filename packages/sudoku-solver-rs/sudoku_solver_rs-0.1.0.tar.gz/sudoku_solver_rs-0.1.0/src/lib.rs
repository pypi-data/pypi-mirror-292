use pyo3::prelude::*;
use sudoku::Sudoku;

fn string_to_9x9_array(s: &str) -> Vec<Vec<u32>> {
    s.chars()
        .collect::<Vec<char>>()
        .chunks(9)
        .map(|chunk| chunk.iter().map(|&c| c.to_digit(10).unwrap()).collect())
        .collect()
}

fn array_9x9_to_string(array: Vec<Vec<u32>>) -> String {
    array
        .iter()
        .flat_map(|row| row.iter())
        .map(|&num| std::char::from_digit(num, 10).unwrap())
        .collect()
}

#[pyfunction]
fn from_str_line(sudoku_line: String) -> PyResult<String> {
    let sudoku = Sudoku::from_str_line(&sudoku_line).unwrap();

    if let Some(solution) = sudoku.solution() {
        return Ok(solution.to_string());
    }
    Ok("".to_string())
}

#[pyfunction]
fn from_num_list(sudoku_list: Vec<Vec<u32>>) -> PyResult<Vec<Vec<u32>>> {
    let sudoku = Sudoku::from_str_line(&array_9x9_to_string(sudoku_list)).unwrap();

    if let Some(solution) = sudoku.solution() {
        return Ok(string_to_9x9_array(&solution.to_string()));
    }
    Ok(Vec::new())
}

#[pymodule]
fn sudoku_solver_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(from_str_line, m)?)?;
    m.add_function(wrap_pyfunction!(from_num_list, m)?)?;
    Ok(())
}
