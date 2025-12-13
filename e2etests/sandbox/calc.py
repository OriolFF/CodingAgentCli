def test_add():
    assert calc.add(1, 2) == 3
    assert calc.add(-1, -2) == -3
    assert calc.add(0, 0) == 0
    assert calc.add(float('inf'), float('-inf')) is None
    # Edge cases
    assert calc.add(-0.0, 0.0) == 0
    assert calc.add(1e36, -1e37) == 0.0
    # Corner cases
    assert calc.add(float('nan'), float('inf')) is None