# Plain-language prompts: before and after samples

Written 2026-10-07 by hack-jedi. One sample per scenario, not a rate. **Before** is the earlier scored run (older code and prompts, `evaluations/results/before_final2` and `evaluations/results/hospital`), not a paired A/B. **After** is one live run on the plain-language prompts. Reading levels use `code/nury/readability.py` (hack-ninja's formulas) on the whole stage text, including any verse: a tripwire, not proof a family understood. The Spanish has not been read by a native speaker.

## Spanish: detention 01 (happy path)

### rights

| | Reading level |
|---|---|
| Before | INFLESZ 76.1, 9.0 words per sentence |
| After | INFLESZ 77.7, 9.2 words per sentence |

**Before**

```
- Tiene derecho a guardar silencio. No tiene que responder preguntas sobre su estatus migratorio ni dónde nació. (ACLU Know Your Rights)
- No abra la puerta a menos que los agentes muestren una orden firmada por un juez con su nombre y dirección correctos. Pida que la pasen por debajo de la puerta. (ACLU Know Your Rights)
- No firme ningún documento sin hablar primero con un abogado. Firmar podría significar renunciar a su derecho a una audiencia. (ACLU Know Your Rights)
- Tiene derecho a hablar con un abogado. Diga claramente que quiere hablar con uno y no responda más preguntas hasta hacerlo. (ACLU Know Your Rights)
- No mienta a los agentes ni muestre documentos falsos. Puede empeorar mucho su situación. (ACLU Know Your Rights)
- Memorice el número de teléfono de una persona de confianza y de un abogado de inmigración. Deje copias de documentos importantes con alguien de confianza. (ACLU Know Your Rights)

Por favor, hable con un abogado de inmigración calificado lo antes posible para recibir orientación sobre su situación específica.
```

**After**

```
El paso más importante ahora mismo es hablar con un abogado de inmigración.

- Tiene derecho a guardar silencio. Usted no tiene que responder preguntas sobre su estado migratorio ni sobre dónde nació. (ACLU Know Your Rights)
- No abra la puerta a menos que los agentes muestren una orden firmada por un juez. Esa orden debe tener su nombre y dirección correctos. Pida que la pasen por debajo de la puerta antes de abrir. (ACLU Know Your Rights)
- No firme ningún documento sin hablar primero con un abogado. Firmar puede significar que usted renuncia a su derecho a una audiencia ante un juez. (ACLU Know Your Rights)
- Tiene derecho a hablar con un abogado. Diga claramente que quiere hablar con uno. No responda más preguntas hasta que pueda hacerlo. (ACLU Know Your Rights)
- No mienta a los agentes ni muestre documentos falsos. Hacer eso puede empeorar mucho su situación. (ACLU Know Your Rights)
- Memorice el número de teléfono de una persona de confianza y de un abogado de inmigración. Deje copias de sus documentos importantes con alguien en quien confíe. (ACLU Know Your Rights)

Por favor, comuníquese con un abogado de inmigración lo antes posible para que pueda orientarle según su situación específica.
```

### checklist

| | Reading level |
|---|---|
| Before | INFLESZ 63.6, 10.0 words per sentence |
| After | INFLESZ 69.1, 8.9 words per sentence |

**Before**

```
DO TONIGHT / HAGA ESTA NOCHE

1. Llame a un abogado de inmigración calificado ahora mismo. Esto es lo más importante que puede hacer esta noche.
2. Pregúntele al abogado cómo averiguar en qué instalación está Jose.
3. Pregúntele al abogado si Jose tiene algún caso migratorio abierto o trámite legal anterior que el abogado deba conocer.
4. Memorice un número de teléfono de una persona de confianza. Asegúrese de que Jose también lo tenga memorizado si puede comunicarse con usted.
5. Deje copias de los documentos importantes con una persona de confianza esta noche.
6. Escriba una lista de preguntas para el abogado antes de llamar.

---

DO NOT DO / NO HAGA ESTA NOCHE

1. No abra la puerta si llegan agentes, a menos que muestren una orden firmada por un juez con el nombre y la dirección correctos. Pida que la pasen por debajo de la puerta.
2. No firme ningún documento sin hablar primero con un abogado. Firmar podría significar renunciar al derecho a una audiencia.
3. No mienta a los agentes ni muestre documentos falsos. Puede empeorar mucho la situación.
4. No responda preguntas sobre su estatus migratorio ni dónde nació. Tiene derecho a guardar silencio.

---

GATHER THESE DOCUMENTS / REÚNA ESTOS DOCUMENTOS

- Identificaciones de todos los miembros de la familia, incluyendo las de los niños
- Documentos migratorios de Jose, si los tiene en casa
- Número de caso migratorio, si existe
- Actas de nacimiento de los niños
- Cualquier papel relacionado con trámites legales anteriores de Jose
- El número de teléfono del abogado de inmigración
- El número de teléfono de Maria y de otra persona de confianza

---

*Nury es un asistente de IA, no es abogado, pastor, consejero ni terapeuta. Esto es información legal general, no asesoramiento legal. Por favor revísela con un abogado de inmigración calificado lo antes posible.*
```

**After**

```
DO TONIGHT / QUÉ HACER ESTA NOCHE

1. Llame a un abogado de inmigración ahora mismo.
2. Pregúntele al abogado cómo averiguar dónde está Jose.
3. Memorice el número de teléfono del abogado y de una persona de confianza.
4. Deje copias de sus documentos importantes con alguien de confianza.
5. Si alguien toca la puerta, pida que muestren la orden por debajo de la puerta antes de abrir.

DO NOT DO / QUÉ NO HACER

1. No firme ningún documento sin hablar primero con un abogado.
2. No abra la puerta si los agentes no muestran una orden firmada por un juez.
3. No responda preguntas sobre su estado migratorio ni sobre dónde nació.
4. No muestre documentos falsos ni diga información que no sea verdad.

GATHER THESE DOCUMENTS / DOCUMENTOS QUE DEBE REUNIR

- Identificación de Jose y de Maria
- Documentos migratorios de Jose
- Actas de nacimiento de los niños
- Cualquier papel que los agentes hayan dejado ayer
- El número de teléfono del abogado y de una persona de confianza
- Preguntas escritas para el abogado, como: ¿Dónde está Jose? ¿Qué podemos hacer ahora?

---

Nury es un asistente de IA, no es abogado, pastor, consejero ni terapeuta. Esto es información legal general, no asesoramiento legal. Por favor revísela con un abogado de inmigración calificado lo antes posible.
```

### pastoral

| | Reading level |
|---|---|
| Before | INFLESZ 90.2, 7.4 words per sentence |
| After | INFLESZ 75.8, 7.2 words per sentence |

**Before**

```
VERSE: psa23_4

WHY: Este salmo habla de no estar solos en los momentos más difíciles, de que hay compañía y sostén aun en lo más oscuro. Eso es lo que ustedes están viviendo ahora.

MESSAGE: Maria, sabemos que esta noche es muy difícil. El miedo que siente es real, y lo entendemos. La iglesia está con usted y con sus hijos. Tenemos lista una lista de personas a las que puede llamar y un resumen de pasos para esta noche. Si quiere orar juntos, puede llamar. No está sola.
```

**After**

```
VERSE: psa46_1

WHY: Este versículo habla de un refugio firme en los momentos difíciles. Ustedes no están solos en lo que están viviendo.

MESSAGE: Querida familia, no están solos. La iglesia está con ustedes y piensa en ustedes en este momento. Sabemos que tienen miedo, y eso es completamente entendible. En este paquete hay una lista de pasos para esta noche y una lista de personas a quienes pueden contactar. Lo más importante ahora mismo es hablar con un abogado de inmigración. Si quieren orar juntos o hablar, pueden llamar. Estamos con ustedes.
```

## English: hospital h08 (English-speaking family)

### info

| | Reading level |
|---|---|
| Before | grade 11.6, 18.8 words per sentence |
| After | grade 7.5, 14.2 words per sentence |

**Before**

```
- A hospital may share health information with a family member or close friend who is involved in the patient's care, but only what is directly relevant to that involvement. If the patient is present and able to decide, the hospital may share when the patient agrees, when the patient has the chance to object and does not, or when the hospital reasonably infers from the circumstances that the patient does not object. (HIPAA rule 45 CFR 164.510(b))
- If the patient is not present, or cannot agree because of incapacity, the hospital may use its professional judgment to decide whether sharing is in the patient's best interests, and may share only information directly relevant to the person's involvement. (HIPAA rule 45 CFR 164.510(b))
- The patient, or the patient's representative as state law allows, has the right to make informed decisions about care. This includes being told about the patient's health status, being involved in care planning and treatment, and being able to request or refuse treatment. (Hospital patient rights rule 42 CFR 482.13)
- The hospital must tell each patient, or a support person, about visitation rights, including any clinical restriction on them. The patient may choose which visitors to receive and may withdraw that consent at any time. The hospital may not deny visitation because of race, color, national origin, religion, sex, gender identity, sexual orientation, or disability. (Hospital patient rights rule 42 CFR 482.13)
- A covered hospital must offer a qualified interpreter to a person with limited English proficiency at no charge. The service must be accurate and timely. The hospital cannot require the person to bring or pay for their own interpreter, should not rely on a minor child to interpret except as a temporary emergency measure, and may use an accompanying adult only as a temporary emergency measure or when the person specifically asks. (Language access rule 45 CFR 92.201)
- The hospital must have a process for prompt resolution of patient complaints, and must tell each patient whom to contact to file one. When a grievance is resolved, the hospital must give the patient written notice with the contact person's name, the steps taken, the results, and the date it was finished. (Hospital patient rights rule 42 CFR 482.13)

Please ask the hospital care team any questions you have about Carol and her care.
```

**After**

```
The care team at the hospital can answer your questions about Carol.

- Ask the care team what health information they can share with you as her husband; a hospital may share information with a family member involved in the patient's care, but only what is directly relevant to your involvement. (HIPAA rule 45 CFR 164.510(b))
- Ask the care team what they can share if Carol is not able to speak for herself right now; the hospital may use its professional judgment to decide what to share when a patient cannot be asked. (HIPAA rule 45 CFR 164.510(b))
- Ask the care team about Carol's right to be informed and to take part in decisions about her care; she, or her representative as state law allows, has the right to be told about her health status, to be involved in care planning, and to request or refuse treatment. (Hospital patient rights rule 42 CFR 482.13)
- Ask the care team about visitation rules in the ICU; the hospital must tell you about visitation rights and any clinical limits on visits, and Carol may choose which visitors she wants to receive. (Hospital patient rights rule 42 CFR 482.13)
- Ask whether anyone in your family or group needs an interpreter; the hospital must provide a free, qualified interpreter to anyone who needs one, and it cannot ask you to bring your own or pay for one. (Language access rule 45 CFR 92.201)
- Write down any concerns you have about your care or Carol's care; the hospital must have a process to resolve patient complaints, and must tell you who to contact and give you written notice of the outcome. (Hospital patient rights rule 42 CFR 482.13)

Please ask the hospital care team directly about Carol and her care.
```

### checklist

| | Reading level |
|---|---|
| Before | grade 5.6, 10.3 words per sentence |
| After | grade 4.6, 10.1 words per sentence |

**Before**

```
## DO TONIGHT

1. Ask the ICU care team for the name of the doctor or nurse leading Carol's care, and ask for a phone number you can call for updates.

2. Write down every staff name and any information the care team shares with you. A pen and paper help.

3. Ask the care team to explain your visitation rights and any limits that may apply in the ICU.

4. Ask the care team how you, as Carol's husband, can receive information about her care.

5. Ask the care team how to reach the hospital social worker. A social worker can help you understand what is happening and find support.

6. Ask the care team who to contact if you have a complaint or concern about Carol's care.

---

## DO NOT DO

1. Do not assume the hospital can share all information with you. The hospital shares only what is directly relevant to your involvement in Carol's care.

---

## WHAT TO BRING AND ASK

**Bring or have ready:**

- Carol's full name
- Her location: Valley General Hospital, ICU, and her room number if you know it
- Your name and relationship: Dan Whitfield, husband
- A pen and paper to write down staff names, phone numbers, and information
- A written list of your questions before you speak with the care team

**Ask the care team:**

- Who is leading Carol's care, and what is the best number to call for updates?
- What are the visitation hours and rules for the ICU?
- How can I, as her husband, receive information about her care?
- Is a hospital social worker available, and how do I reach them?
- Who do I contact if I have a concern or complaint about her care?

---

*Nury is an AI assistant, not a doctor, nurse, lawyer, pastor, counselor, or therapist. This is general information, not medical or legal advice. Please ask the hospital care team about Carol and her care.*
```

**After**

```
DO TONIGHT

1. Ask the care team which nurse or doctor is in charge of Carol's care.
2. Ask what health information they can share with you as her husband.
3. Ask what they can share if Carol is not able to speak for herself right now.
4. Ask the care team about visitation rules in the ICU.
5. Ask who to contact if you have a concern about Carol's care.
6. Write down the name of every staff member you speak with tonight.

---

DO NOT DO

Do not assume the hospital can share everything about Carol's care with you.
Do not rely on a child to interpret for you; the hospital must provide a free qualified interpreter.

---

WHAT TO BRING AND ASK

**Bring or have ready:**
- Carol's full name and the unit she is in (ICU at Valley General)
- Your name and your relationship to her
- A pen and paper to write down staff names and what you are told
- A written list of your questions before you speak with the care team

**Ask the care team:**
- "What can you share with me about Carol's care as her husband?"
- "What can you share if she is not able to speak for herself right now?"
- "What are the visitation rules here in the ICU?"
- "Does Carol have the right to take part in decisions about her care?"
- "Who do I contact if I have a concern about her care?"
- "Can you provide a free interpreter if I need one?"

---

Nury is an AI assistant, not a doctor, nurse, lawyer, pastor, counselor, or therapist. This is general information, not medical or legal advice. Please ask the hospital care team about Carol.
```

### pastoral

| | Reading level |
|---|---|
| Before | grade 2.0, 6.3 words per sentence |
| After | grade 2.1, 7.4 words per sentence |

**Before**

```
VERSE: psa46_1

WHY: You are in a frightening place right now. This verse says God is a refuge and a very present help in trouble.

MESSAGE: Dan Whitfield, we are with you. We know this is a frightening time, and we are thinking of you and Carol. You are not alone in this. The church is standing with you both. A checklist for tonight and a list of hospital resources are ready in this case. Please lean on them. You can call the pastor anytime. We are here.
```

**After**

```
VERSE: psa46_1

WHY: You are in a hard and frightening place right now. This verse says that God is a present help in trouble, and that is where you are.

MESSAGE: Dan Whitfield, you are not alone in this. We know how frightening it is to be in that waiting room. Your heart is carrying a heavy load right now. The church is with you and with Carol. We are thinking of you both, and of your children too. A checklist for tonight and a list of hospital resources are ready in this case. You can call the pastor anytime. We are here.
```
