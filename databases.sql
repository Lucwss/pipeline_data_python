CREATE TABLE product (
        produto VARCHAR NOT NULL,
        categoria_do_produto VARCHAR NOT NULL,
        "preço" FLOAT NOT NULL,
        frete FLOAT NOT NULL,
        data_da_compra TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        vendedor VARCHAR NOT NULL,
        local_da_compra VARCHAR NOT NULL,
        "avaliação_da_compra" INTEGER NOT NULL,
        tipo_de_pagamento VARCHAR NOT NULL,
        quantidade_de_parcelas INTEGER NOT NULL,
        latitude INTEGER NOT NULL,
        longitude INTEGER NOT NULL,
        id SERIAL NOT NULL,
        PRIMARY KEY (id)
)