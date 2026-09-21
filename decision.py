"""Un motor de decisión pequeño y explícito. Sin modelos ni servicios externos."""

CRITERIA = {
    "minimize": "Minimizar víctimas",
    "nonintervention": "No intervenir",
    "protect_main": "Proteger la vía principal",
}


def decide(main: int, branch: int, criterion: str = "minimize") -> dict:
    """Evalúa ambas acciones bajo consecuencias ciertas en este mundo simplificado.

    Empates: mantener la vía. La etiqueta no_intervenir es una regla del ejercicio,
    no una descripción exhaustiva de una teoría ética.
    """
    for value in (main, branch):
        if type(value) is not int or not 0 <= value <= 12:
            raise ValueError("Cada vía debe tener un entero entre 0 y 12 personas.")
    if criterion not in CRITERIA:
        raise ValueError("Criterio desconocido.")

    if criterion == "minimize":
        divert = branch < main
        reason = (
            f"{branch} < {main}: desviar reduce las víctimas previstas."
            if divert else
            f"{main} <= {branch}: mantener no aumenta las víctimas previstas. "
            + ("En empate, esta regla conserva la vía." if main == branch else "")
        )
        rule = "desviar = personas_desvio < personas_principal"
    elif criterion == "nonintervention":
        divert = False
        reason = "La regla prohíbe accionar la palanca, con independencia del recuento."
        rule = "desviar = False"
    else:
        divert = main > 0
        reason = (
            "Hay personas en la vía principal: la regla prioriza protegerlas, "
            "aunque el desvío tenga más personas."
            if divert else "No hay personas en la vía principal: se conserva la vía."
        )
        rule = "desviar = personas_principal > 0"

    return {
        "action": "divert" if divert else "keep",
        "criterion": criterion,
        "label": CRITERIA[criterion],
        "reason": reason.strip(),
        "rule": rule,
        "victims": branch if divert else main,
        "safe": main if divert else branch,
        "alternatives": {"keep": main, "divert": branch},
    }
