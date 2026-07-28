"""Tests for the Euler buckling critical load calculator."""
import json
import math
import pytest
import engineering_calculator.calculators.euler_buckling as module
from engineering_calculator.calculators.euler_buckling import calculate_euler_buckling


def base():
    return dict(elastic_modulus_value=200, elastic_modulus_unit="GPa",
                second_moment_of_area_value=8_000_000,
                second_moment_of_area_unit="mm^4",
                unsupported_length_value=3, unsupported_length_unit="m",
                effective_length_factor=1, output_unit="kN")


def load(args):
    return calculate_euler_buckling(**args)["results"]["critical_load"]["value"]


def test_si_reference_and_reverse_verification():
    result = calculate_euler_buckling(**base())
    assert result["results"]["critical_load"] == {"value": pytest.approx(1754.596337971441), "unit": "kN"}
    p = result["results"]["critical_load_newtons"]["value"]
    assert p == pytest.approx(1_754_596.337971441)
    assert p * 3000**2 / (math.pi**2 * 200_000) == pytest.approx(8_000_000)


def test_us_reference_and_unit_equivalence():
    us = calculate_euler_buckling(29_000, "ksi", 10, "in^4", 120, "in", 1, "kip")
    assert us["results"]["critical_load"] == {"value": pytest.approx(198.762866410827), "unit": "kip"}
    si = calculate_euler_buckling(29_000 * 6.894757293168361, "MPa",
        10 * 416_231.4256, "mm^4", 120 * 25.4, "mm", 1, "N")
    assert us["results"]["critical_load_newtons"]["value"] == pytest.approx(si["results"]["critical_load_newtons"]["value"])


@pytest.mark.parametrize("name,ratio", [("elastic_modulus_value", 2), ("second_moment_of_area_value", 2),
                                        ("effective_length_factor", .25), ("unsupported_length_value", .25)])
def test_sensitivity(name, ratio):
    original = load(base()); changed = base(); changed[name] *= 2
    assert load(changed) / original == pytest.approx(ratio)


@pytest.mark.parametrize("value,unit", [(1e6,"Pa"),(1000,"kPa"),(1,"MPa"),(.001,"GPa"),
    (1/.006894757293168361,"psi"),(1/6.894757293168361,"ksi")])
def test_modulus_units(value, unit):
    assert calculate_euler_buckling(value,unit,1,"mm^4",1,"mm",1,"N")["results"]["critical_load"]["value"] == pytest.approx(math.pi**2)


@pytest.mark.parametrize("value,unit", [(1,"mm^4"),(1e-4,"cm^4"),(1e-12,"m^4"),(1/416231.4256,"in^4")])
def test_second_moment_units(value, unit):
    assert calculate_euler_buckling(1,"MPa",value,unit,1,"mm",1,"N")["results"]["critical_load"]["value"] == pytest.approx(math.pi**2)


@pytest.mark.parametrize("value,unit", [(1,"mm"),(.1,"cm"),(.001,"m"),(1/25.4,"in")])
def test_length_units(value, unit):
    assert calculate_euler_buckling(1,"MPa",1,"mm^4",value,unit,1,"N")["results"]["critical_load"]["value"] == pytest.approx(math.pi**2)


@pytest.mark.parametrize("unit,factor", [("N",1),("kN",1e-3),("MN",1e-6),("lbf",.22480894387096072),("kip",.00022480894387096072)])
def test_output_units(unit, factor):
    result = calculate_euler_buckling(1,"MPa",1,"mm^4",1,"mm",1,unit)
    assert result["results"]["critical_load"] == {"value": pytest.approx(math.pi**2*factor), "unit": unit}


def test_ft_is_rejected():
    with pytest.raises(ValueError, match="unsupported unsupported_length_unit"):
        calculate_euler_buckling(1,"MPa",1,"mm^4",1,"ft",1)


@pytest.mark.parametrize("name", ["elastic_modulus_value","second_moment_of_area_value","unsupported_length_value","effective_length_factor"])
@pytest.mark.parametrize("value", [0,-1])
def test_positive_inputs(name, value):
    args=base(); args[name]=value
    with pytest.raises(ValueError, match=f"{name} must be greater than zero"):
        calculate_euler_buckling(**args)


@pytest.mark.parametrize("name", ["elastic_modulus_value","second_moment_of_area_value","unsupported_length_value","effective_length_factor"])
@pytest.mark.parametrize("value", [True,"x",None])
def test_invalid_numeric_types(name, value):
    args=base(); args[name]=value
    with pytest.raises(TypeError, match=f"{name} must be a real number"):
        calculate_euler_buckling(**args)


@pytest.mark.parametrize("name", ["elastic_modulus_value","second_moment_of_area_value","unsupported_length_value","effective_length_factor"])
@pytest.mark.parametrize("value", [float("nan"),float("inf"),-float("inf")])
def test_nonfinite_inputs(name, value):
    args=base(); args[name]=value
    with pytest.raises(ValueError, match=f"{name} must be finite"):
        calculate_euler_buckling(**args)


@pytest.mark.parametrize("name,value,error", [("elastic_modulus_unit",None,TypeError),("second_moment_of_area_unit",1,TypeError),
    ("unsupported_length_unit",None,TypeError),("output_unit",1,TypeError),("elastic_modulus_unit","bar",ValueError),
    ("second_moment_of_area_unit","mm^2",ValueError),("unsupported_length_unit","yd",ValueError),("output_unit","kgf",ValueError)])
def test_invalid_units(name, value, error):
    args=base(); args[name]=value
    with pytest.raises(error, match=name): calculate_euler_buckling(**args)


def test_oversized_integer_and_missing_input():
    args=base(); args["elastic_modulus_value"]=10**400
    with pytest.raises(ValueError, match="representable as a finite float"): calculate_euler_buckling(**args)
    with pytest.raises(TypeError, match="effective_length_factor"): calculate_euler_buckling(200,"GPa",8e6,"mm^4",3,"m")


@pytest.mark.parametrize("changes,message", [
    ({"elastic_modulus_value":1e308,"elastic_modulus_unit":"GPa"},"converted elastic modulus must be finite"),
    ({"elastic_modulus_value":5e-324,"elastic_modulus_unit":"Pa"},"converted elastic modulus must be greater than zero"),
    ({"unsupported_length_value":1e308,"unsupported_length_unit":"mm","effective_length_factor":2},"effective length must be finite"),
    ({"unsupported_length_value":5e-324,"unsupported_length_unit":"mm","effective_length_factor":.5},"effective length must be greater than zero"),
    ({"unsupported_length_value":1e200,"unsupported_length_unit":"mm"},"squared effective length must be finite"),
    ({"unsupported_length_value":1e-200,"unsupported_length_unit":"mm"},"squared effective length must be greater than zero"),
    ({"elastic_modulus_value":1e200,"elastic_modulus_unit":"MPa","second_moment_of_area_value":1e200},"flexural rigidity must be finite"),
    ({"elastic_modulus_value":1e200,"elastic_modulus_unit":"MPa","second_moment_of_area_value":1e108},"Euler critical load numerator must be finite"),
    ({"elastic_modulus_value":1e150,"elastic_modulus_unit":"MPa","second_moment_of_area_value":1e150,"unsupported_length_value":1e-4,"unsupported_length_unit":"mm"},"calculated Euler critical load must be finite"),
    ({"elastic_modulus_value":1e-150,"elastic_modulus_unit":"MPa","second_moment_of_area_value":1e-150,"unsupported_length_value":1e20,"unsupported_length_unit":"mm"},"calculated Euler critical load must be greater than zero")])
def test_numerical_boundaries(changes, message):
    args=base(); args.update(changes)
    with pytest.raises(ValueError, match=message): calculate_euler_buckling(**args)


def test_numerator_underflow(monkeypatch):
    monkeypatch.setattr(module.math,"pi",1e-200)
    with pytest.raises(ValueError, match="Euler critical load numerator must be greater than zero"):
        calculate_euler_buckling(1e-100,"MPa",1,"mm^4",1,"mm",1)


@pytest.mark.parametrize("factor,message", [(1e308,"converted Euler critical load must be finite"),(5e-324,"converted Euler critical load must be greater than zero")])
def test_output_boundaries(monkeypatch, factor, message):
    monkeypatch.setitem(module._NEWTONS_TO_OUTPUT,"N",factor)
    modulus = 0.01 if factor < 1 else 1
    with pytest.raises(ValueError, match=message): calculate_euler_buckling(modulus,"MPa",1,"mm^4",1,"mm",1,"N")


def test_contract_metadata_warnings_and_content():
    result=calculate_euler_buckling(**base())
    assert set(result)=={"calculator","inputs","results","governing_equation","assumptions","warnings","limitations","references"}
    assert result["calculator"]=={"id":"stability.euler_buckling","name":"Euler Buckling Critical Load Calculator","version":"0.1.0",
        "category":"Stability Analysis","engineering_domain":"Structural Stability / Mechanics of Materials",
        "purpose":"Calculate the ideal elastic critical buckling load of a slender, straight column using Euler buckling theory",
        "reference_equation":"L_eff = K * L; P_cr = pi^2 * E * I / L_eff^2"}
    assert result["results"]["effective_length_mm"]=={"value":3000.0,"unit":"mm"}
    assert result["results"]["critical_load_newtons"]["unit"]=="N"
    assert "caller-supplied second moment of area" in result["results"]["buckling_axis_traceability"]
    assert result["warnings"] == [
        "Euler buckling is valid only for sufficiently slender columns that remain elastic up to buckling.",
        "The supplied second moment of area must correspond to the actual buckling axis.",
        "The effective length factor depends on real end restraints and may differ from idealized textbook values.",
        "The calculator does not determine whether yielding or inelastic buckling occurs first.",
        "The result is an ideal theoretical critical load, not an allowable design load.",
    ]
    assert result["assumptions"] and result["limitations"] and result["references"]


def test_substitution_precision():
    assert calculate_euler_buckling(**base())["governing_equation"]["substitution"] == (
        "L_eff = 1 * 3000 mm = 3000 mm; P_cr = pi^2 * (200000 MPa) * "
        "(8000000 mm^4) / (3000 mm)^2 = 1754596.3379714414 N")


def test_json_and_determinism():
    first=calculate_euler_buckling(**base()); second=calculate_euler_buckling(**base())
    assert json.loads(json.dumps(first))==first
    assert first==second
