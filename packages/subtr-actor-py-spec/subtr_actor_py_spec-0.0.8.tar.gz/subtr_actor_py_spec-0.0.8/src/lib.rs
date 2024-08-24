use numpy::ndarray::Axis;
use numpy::pyo3::IntoPy;
use numpy::IntoPyArray;
use pyo3::prelude::*;
use pyo3::*;
use serde_json::{json, Value};
use types::PyDict;
use std::collections::BTreeMap;
use std::path::PathBuf;
use subtr_actor_spec::*;

#[pyfunction]
fn parse_replay<'p>(py: Python<'p>, data: &[u8]) -> PyResult<PyObject> {
    let replay = serde_json::to_value(replay_from_data(data)?).map_err(to_py_error)?;
    Ok(convert_to_py(py, &replay))
}

fn shots_from_data<'p>(data: &[u8]) -> SubtrActorResult<(Vec<ShotMetadata>, Vec<Vec<f32>>, Vec<String>)> {
    let parsing = boxcars::ParserBuilder::new(&data[..])
    .always_check_crc()
    .must_parse_network_data()
    .parse();

    let replay = parsing.unwrap();

    let mut collector = NDArrayCollector::<f32>::from_strings(
        &["InterpolatedBallRigidBodyNoVelocities"],
        &[
            "InterpolatedPlayerRigidBodyNoVelocities",
            "PlayerBoost",
            "PlayerAnyJump",
            "PlayerDemolishedBy",
        ],
    )
    .unwrap();

    let mut collector2 = NDArrayCollector::<f32>::from_strings(
        &["InterpolatedBallRigidBodyNoVelocities"],
        &[
            "InterpolatedPlayerRigidBodyNoVelocities",
            "PlayerBoost",
            "PlayerAnyJump",
            "PlayerDemolishedBy",
        ],
    )
    .unwrap();

    FrameRateDecorator::new_from_fps(10.0, &mut collector)
    .process_replay(&replay)
    .unwrap();

    let (meta, array) = collector.get_meta_and_ndarray().unwrap();

    let result = collector2.process_and_get_meta_and_headers(&replay).unwrap();

    // Extract the shots metadata
    let shots = result.replay_meta.shots.clone();  
    let json_array: Vec<Vec<f32>> = array
    .axis_iter(Axis(0))
    .map(|row| row.to_vec())
    .collect();

    // Pass the `Value` reference to `convert_to_py`
    Ok((shots, json_array, meta.headers_vec()))
}

fn replay_from_data(data: &[u8]) -> PyResult<boxcars::Replay> {
    boxcars::ParserBuilder::new(data)
        .must_parse_network_data()
        .on_error_check_crc()
        .parse()
        .map_err(to_py_error)
}

#[pymodule]
#[pyo3(name = "subtr_actor_spec")]
fn subtr_actor_module(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(parse_replay))?;
    m.add_wrapped(wrap_pyfunction!(get_ndarray_with_info_from_replay_filepath))?;
    m.add_wrapped(wrap_pyfunction!(get_data))?;
    m.add_wrapped(wrap_pyfunction!(get_replay_meta))?;
    m.add_wrapped(wrap_pyfunction!(get_column_headers))?;
    m.add_wrapped(wrap_pyfunction!(get_replay_frames_data))?;
    Ok(())
}

fn to_py_error<E: std::error::Error>(e: E) -> PyErr {
    PyErr::new::<exceptions::PyException, _>(format!("{}", e))
}

fn handle_frames_exception(e: subtr_actor_spec::SubtrActorError) -> PyErr {
    PyErr::new::<exceptions::PyException, _>(format!("{:?} {}", e.variant, e.backtrace.to_string()))
}

fn convert_to_py(py: Python, value: &Value) -> PyObject {
    match value {
        Value::Null => py.None(),
        Value::Bool(b) => b.into_py(py),
        Value::Number(n) => match n {
            n if n.is_u64() => n.as_u64().unwrap().into_py(py),
            n if n.is_i64() => n.as_i64().unwrap().into_py(py),
            n if n.is_f64() => n.as_f64().unwrap().into_py(py),
            _ => py.None(),
        },
        Value::String(s) => s.into_py(py),
        Value::Array(list) => {
            let list: Vec<PyObject> = list.iter().map(|e| convert_to_py(py, e)).collect();
            list.into_py(py)
        }
        Value::Object(m) => {
            let mut map = BTreeMap::new();
            m.iter().for_each(|(k, v)| {
                map.insert(k, convert_to_py(py, v));
            });
            map.into_py(py)
        }
    }
}

static DEFAULT_GLOBAL_FEATURE_ADDERS: [&str; 1] = ["BallRigidBody"];

static DEFAULT_PLAYER_FEATURE_ADDERS: [&str; 3] =
    ["PlayerRigidBody", "PlayerBoost", "PlayerAnyJump"];

/// Convert a replay file to a `numpy` ndarray with additional metadata in Python.
///
/// This function takes a replay file path, reads the file and processes it. It
/// constructs an ndarray with global and player features and collects metadata
/// about the replay. The constructed ndarray and metadata are then converted
/// into Python objects and returned.
///
/// The replay file processing can optionally be run at a different
/// frames-per-second (fps) rate. By default, it processes replays at 10 fps.
///
/// # Arguments
///
/// * `py`: A Python interpreter instance.
/// * `filepath`: A path to the replay file.
/// * `global_feature_adders`: An optional vector of global feature adders. Each
/// adder is a string that represents a feature to be added to the global
/// features ndarray.
/// * `player_feature_adders`: An optional vector of player feature adders. Each
/// adder is a string that represents a feature to be added to the player
/// features ndarray.
/// * `fps`: An optional float representing the frames-per-second to use when
/// processing the replay. Default is 10.0 fps.
///
/// Refer to the [struct definitions provided in the ndarray
/// collector](https://docs.rs/subtr-actor/latest/subtr_actor/collector/ndarray/index.html)
/// documentation for valid string names to use within the global_feature_adders
/// and player_feature_adders arguments. These strings correspond to the
/// features that will be added to the global and player ndarrays respectively.
///
///
/// # Returns
///
/// * A Python tuple containing metadata about the replay and the ndarray of
/// features. If there was an error reading the file or processing the replay,
/// this will be an Err variant with the Python error.
#[pyfunction]
fn get_ndarray_with_info_from_replay_filepath<'p>(
    py: Python<'p>,
    filepath: PathBuf,
    global_feature_adders: Option<Vec<String>>,
    player_feature_adders: Option<Vec<String>>,
    fps: Option<f32>,
) -> PyResult<PyObject> {
    let data = std::fs::read(filepath.as_path()).map_err(to_py_error)?;
    let replay = replay_from_data(&data)?;

    let mut collector = build_ndarray_collector(global_feature_adders, player_feature_adders)
        .map_err(handle_frames_exception)?;

    FrameRateDecorator::new_from_fps(fps.unwrap_or(10.0), &mut collector)
        .process_replay(&replay)
        .map_err(handle_frames_exception)?;

    let (replay_meta_with_headers, rust_nd_array) = collector
        .get_meta_and_ndarray()
        .map_err(handle_frames_exception)?;

    let python_replay_meta = convert_to_py(
        py,
        &serde_json::to_value(&replay_meta_with_headers).map_err(to_py_error)?,
    );

    let python_nd_array = rust_nd_array.into_pyarray(py);
    Ok((python_replay_meta, python_nd_array).into_py(py))
}

fn build_ndarray_collector(
    global_feature_adders: Option<Vec<String>>,
    player_feature_adders: Option<Vec<String>>,
) -> subtr_actor_spec::SubtrActorResult<subtr_actor_spec::NDArrayCollector<f32>> {
    let global_feature_adders = global_feature_adders.unwrap_or_else(|| {
        DEFAULT_GLOBAL_FEATURE_ADDERS
            .iter()
            .map(|i| i.to_string())
            .collect()
    });
    let player_feature_adders = player_feature_adders.unwrap_or_else(|| {
        DEFAULT_PLAYER_FEATURE_ADDERS
            .iter()
            .map(|i| i.to_string())
            .collect()
    });
    let global_feature_adders: Vec<&str> = global_feature_adders.iter().map(|s| &s[..]).collect();
    let player_feature_adders: Vec<&str> = player_feature_adders.iter().map(|s| &s[..]).collect();
    subtr_actor_spec::NDArrayCollector::<f32>::from_strings(
        &global_feature_adders,
        &player_feature_adders,
    )
}

fn shot_to_py_obj(py: Python, shot: &ShotMetadata) -> PyObject {
    let shot_dict = PyDict::new(py);

    shot_dict.set_item("shooter", shot.shooter.clone()).unwrap();
    shot_dict.set_item("frame", shot.frame).unwrap();
    shot_dict.set_item("ball_position", shot.ball_position).unwrap();
    shot_dict.set_item("ball_linear_velocity", shot.ball_linear_velocity).unwrap();
    shot_dict.set_item("ball_angular_velocity", shot.ball_angular_velocity).unwrap();

    shot_dict.into_py(py)
}

#[pyfunction]
fn get_data<'p>(
    py: Python<'p>,
    filepath: PathBuf,
) -> PyResult<PyObject> {
    let data = std::fs::read(filepath.as_path()).map_err(to_py_error)?;

    let replay: (Vec<ShotMetadata>, Vec<Vec<f32>>, Vec<String>) = shots_from_data(&data).map_err(handle_frames_exception)?;

    let (shots, array, headers) = replay;

    let py_shots: Vec<PyObject> = shots.iter()
    .map(|shot| shot_to_py_obj(py, shot))
    .collect();

    let py_array = array.into_py(py);
    let py_headers = headers.into_py(py);

    Ok((py_shots, py_array, py_headers).into_py(py))
}

#[pyfunction]
fn get_replay_meta<'p>(
    py: Python<'p>,
    filepath: PathBuf,
    global_feature_adders: Option<Vec<String>>,
    player_feature_adders: Option<Vec<String>>,
) -> PyResult<PyObject> {
    let data = std::fs::read(filepath.as_path()).map_err(to_py_error)?;
    let replay = replay_from_data(&data)?;

    let mut collector = build_ndarray_collector(global_feature_adders, player_feature_adders)
        .map_err(handle_frames_exception)?;

    let replay_meta = collector
        .process_and_get_meta_and_headers(&replay)
        .map_err(handle_frames_exception)?;

    Ok(convert_to_py(
        py,
        &serde_json::to_value(&replay_meta).map_err(to_py_error)?,
    ))
}

#[pyfunction]
fn get_column_headers<'p>(
    py: Python<'p>,
    global_feature_adders: Option<Vec<String>>,
    player_feature_adders: Option<Vec<String>>,
) -> PyResult<PyObject> {
    let header_info = build_ndarray_collector(global_feature_adders, player_feature_adders)
        .map_err(handle_frames_exception)?
        .get_column_headers();
    Ok(convert_to_py(
        py,
        &serde_json::to_value(&header_info).map_err(to_py_error)?,
    ))
}

#[pyfunction]
fn get_replay_frames_data<'p>(py: Python<'p>, filepath: PathBuf) -> PyResult<PyObject> {
    let data = std::fs::read(filepath.as_path()).map_err(to_py_error)?;
    let replay = replay_from_data(&data)?;

    let replay_data = subtr_actor_spec::ReplayDataCollector::new()
        .get_replay_data(&replay)
        .map_err(handle_frames_exception)?;

    Ok(convert_to_py(
        py,
        &serde_json::to_value(replay_data).map_err(to_py_error)?,
    ))
}
