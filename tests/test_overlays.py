import numpy as np

from analog_image_generator import geologic_generators as gg


def _build_base_masks(shape=(64, 64)):
    rng = np.random.default_rng(1)
    masks = {
        "channel": (rng.random(shape) > 0.6).astype(np.float32),
        "floodplain": (rng.random(shape) > 0.3).astype(np.float32),
        "overbank": (rng.random(shape) > 0.4).astype(np.float32),
    }
    return masks


def test_channel_fill_sandstone_nonzero_and_aligned():
    gray = np.zeros((64, 64), dtype=np.float32)
    masks = _build_base_masks()
    rng = gg.utils.seeded_rng(10)
    updated, masks = gg.channel_fill_sandstone(gray, masks, rng)
    assert masks["channel_fill"].shape == gray.shape
    assert masks["channel_fill"].dtype == np.float32
    assert masks["channel_fill"].sum() > 0
    assert np.all((updated >= 0.0) & (updated <= 1.0))


def test_cross_bedding_styles_vary():
    mask = np.ones((64, 64), dtype=np.float32)
    rng = gg.utils.seeded_rng(15)
    planar = gg.apply_cross_bedding(mask, "planar", rng)
    rng = gg.utils.seeded_rng(15)
    trough = gg.apply_cross_bedding(mask, "trough", rng)
    assert planar.shape == mask.shape
    assert trough.shape == mask.shape
    assert not np.allclose(planar, trough)


def test_fining_upward_increases_toward_channel():
    channel = np.zeros((64, 64), dtype=np.float32)
    channel[:, 30:34] = 1.0
    floodplain = np.ones_like(channel)
    rng = gg.utils.seeded_rng(21)
    fining, mudstone = gg.fining_upward_and_mudstone(channel, floodplain, rng)
    center_mean = float(fining[:, 31:33].mean())
    edge_mean = float(fining[:, :5].mean())
    assert center_mean > edge_mean
    assert mudstone.mean() > 0


def test_petrology_metadata_sums_to_unity():
    rng = gg.utils.seeded_rng(33)
    masks = {
        "channel_fill": rng.random((32, 32)).astype(np.float32),
        "overbank": rng.random((32, 32)).astype(np.float32),
        "marsh": rng.random((32, 32)).astype(np.float32),
    }
    metadata = gg._petrology_metadata(masks)
    assert abs(sum(metadata["mineralogy"].values()) - 1.0) <= 1.5e-3
