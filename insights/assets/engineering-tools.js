"use strict";
(() => {
  const fmt = (value, unit) => value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " " + unit;
  function read(form, key, minimum, maximum, integer = false) {
    const input = form.elements.namedItem(key);
    const value = Number(input.value);
    if (!input.value.trim() || !Number.isFinite(value) || value < minimum || value > maximum || (integer && !Number.isInteger(value))) {
      throw new Error("Enter a valid " + key + " value between " + minimum + " and " + maximum + (integer ? " (whole numbers only)." : "."));
    }
    return value;
  }
  function optical(form) {
    const length = read(form, "length", 0, 10000);
    const attenuation = read(form, "attenuation", 0, 10);
    const connectors = read(form, "connectors", 0, 10000, true);
    const connectorLoss = read(form, "connectorLoss", 0, 10);
    const splices = read(form, "splices", 0, 10000, true);
    const spliceLoss = read(form, "spliceLoss", 0, 10);
    const margin = read(form, "margin", 0, 100);
    const available = read(form, "available", 0, 200);
    const required = length * attenuation + connectors * connectorLoss + splices * spliceLoss + margin;
    const headroom = available - required;
    return {
      headline: fmt(required, "dB required"),
      detail: "Remaining optical headroom: " + fmt(headroom, "dB") + ". Simplified budget: " + (headroom >= -1e-9 ? "PASS" : "FAIL") + ".",
      note: "Check receiver overload, wavelength and non-power impairments separately."
    };
  }
  function dispatch(form) {
    const dc = read(form, "storage", 0.01, 100000);
    const dod = read(form, "dod", 1, 100) / 100;
    const efficiency = read(form, "efficiency", 1, 100) / 100;
    const ceiling = read(form, "ceiling", 0.01, 100000);
    const power = read(form, "power", 0.01, 100000);
    const hours = read(form, "hours", 0.01, 100000);
    const available = dc * dod * efficiency;
    const required = power * hours;
    const remaining = available - required;
    const feasible = remaining >= -1e-9 && power <= ceiling;
    return {
      headline: feasible ? "PASS — simplified constraints" : "FAIL — simplified constraints",
      detail: "Usable AC energy: " + fmt(available, "MWh") + ". Required AC energy: " + fmt(required, "MWh") + ". Remaining energy: " + fmt(remaining, "MWh") + ".",
      note: "Power ceiling check: " + (power <= ceiling ? "PASS" : "FAIL") + ". This is not a grid dispatch authorization."
    };
  }
  function connect(id, calculate) {
    const form = document.getElementById(id + "-form");
    const result = document.getElementById(id + "-result");
    if (!form || !result) return;
    form.addEventListener("submit", event => {
      event.preventDefault();
      result.replaceChildren();
      try {
        const value = calculate(form);
        const strong = document.createElement("strong");
        const span = document.createElement("span");
        const note = document.createElement("small");
        strong.textContent = value.headline;
        span.textContent = value.detail;
        note.textContent = value.note;
        result.append(strong, span, note);
        result.dataset.invalid = "false";
      } catch (error) {
        result.textContent = error.message;
        result.dataset.invalid = "true";
      }
    });
  }
  connect("optical", optical);
  connect("dispatch", dispatch);
})();