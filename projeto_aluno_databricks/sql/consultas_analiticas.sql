-- Consulta 1: faturamento total por região
SELECT ds_regiao, SUM(vl_liquido) AS faturamento_total
FROM curated_data_dev.comercial.fato_vendas
GROUP BY ds_regiao
ORDER BY faturamento_total DESC;

-- Consulta 2: pedidos por status
SELECT status_pedido, COUNT(*) AS qt_pedidos
FROM curated_data_dev.comercial.fato_vendas
GROUP BY status_pedido;

-- Consulta 3: ticket médio
SELECT AVG(vl_liquido) AS ticket_medio
FROM curated_data_dev.comercial.fato_vendas;
