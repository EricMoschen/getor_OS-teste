

// ================================
// UTILIDADES
// ================================

// Converte texto BR para centavos (inteiro)
function brParaCentavos(valor) {
    if (!valor) return 0
    valor = valor.toString()
        .replace(/\./g, '')
        .replace(',', '.')
    return Math.round(parseFloat(valor) * 100) || 0
}

// Converte centavos para BRL
function centavosParaBR(valor) {
    return (valor / 100).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    })
}

// Converte texto BR para número decimal
function brParaNumero(valor) {
    if (!valor) return 0
    return parseFloat(valor.toString().replace(',', '.')) || 0
}

// ================================
// MÁSCARA INPUT VALOR HORA
// ================================
document.querySelectorAll('.valor_hora').forEach(input => {

    input.addEventListener('input', () => {

        // Remove tudo que não for número ou vírgula
        let v = input.value.replace(/[^0-9,]/g, '')

        // Permite apenas uma vírgula
        let partes = v.split(',')
        if (partes.length > 2) {
            v = partes[0] + ',' + partes.slice(1).join('')
        }

        input.value = v
        calcular()
    })

})

// ================================
// CÁLCULO PRINCIPAL
// ================================
function calcular() {

    let totalHoras = 0
    let valorTotalCentavos = 0

    let mult50 = brParaNumero(document.getElementById('titulo50').value)
    let mult100 = brParaNumero(document.getElementById('titulo100').value)

    document.querySelectorAll('.linha').forEach(linha => {

        // ========================
        // ENTRADAS
        // ========================
        let valorHoraCent = brParaCentavos(
            linha.querySelector('.valor_hora').value
        )

        let horasNormais = brParaNumero(
            linha.querySelector('.horas_normais').innerText
        )

        let horas50 = brParaNumero(
            linha.querySelector('.horas50').innerText
        )

        let horas100 = brParaNumero(
            linha.querySelector('.horas100').innerText
        )

        // ========================
        // CÁLCULOS (EM CENTAVOS)
        // ========================
        let normaisRS = Math.round(horasNormais * valorHoraCent)
        let rs50 = Math.round(horas50 * (valorHoraCent * mult50))
        let rs100 = Math.round(horas100 * (valorHoraCent * mult100))

        let totalRS = normaisRS + rs50 + rs100

        // ========================
        // SAÍDA FORMATADA
        // ========================
        linha.querySelector('.normais_rs').innerText = centavosParaBR(normaisRS)
        linha.querySelector('.rs50').innerText = centavosParaBR(rs50)
        linha.querySelector('.rs100').innerText = centavosParaBR(rs100)
        linha.querySelector('.total_rs').innerText = centavosParaBR(totalRS)

        totalHoras += horasNormais + horas50 + horas100
        valorTotalCentavos += totalRS
    })

    document.getElementById('total_horas').innerText = totalHoras.toFixed(2)
    document.getElementById('valor_total').innerText = centavosParaBR(valorTotalCentavos)
}

// ================================
// EVENTOS
// ================================
document.addEventListener('input', calcular)
document.getElementById('titulo50').addEventListener('change', calcular)
document.getElementById('titulo100').addEventListener('change', calcular)

// ================================
// IMPRIMIR
// ================================
function imprimir() {
    fetch("{% url 'proximo_orcamento' %}")
        .then(r => r.json())
        .then(data => {
            document.getElementById("numero_orcamento").innerText = data.numero
            window.print()
        })
}

calcular()
