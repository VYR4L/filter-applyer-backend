# Image Processing API

API REST para processamento digital de imagens desenvolvida com FastAPI. Implementa diversos algoritmos clássicos de processamento de imagens, incluindo detecção de bordas, segmentação, filtragem e análise de contornos.

## 🚀 Funcionalidades

### Detecção de Bordas
- **Canny Edge Detection**: Detector de bordas multi-estágio com supressão não-máxima e histerese
- **Marr-Hildreth**: Detecção de bordas usando Laplaciano da Gaussiana (LoG) com zero-crossing

### Segmentação
- **Watershed**: Segmentação baseada em marcadores usando algoritmo de inundação de Meyer
- **Otsu's Method**: Limiarização automática por maximização da variância entre-classes
- **Intensity Segmentation**: Posterização em 5 níveis discretos de intensidade

### Filtragem
- **Box Filter**: Filtro de média para suavização e redução de ruído

### Análise de Contornos
- **Freeman Chain Code**: Codificação de contornos em 8-direções (0-7)
- **Object Count**: Contagem de objetos usando CCL ou Freeman Chain Code

## 📁 Estrutura do Projeto

```
implementation/
├── api/
│   └── routes/              # Definições das rotas FastAPI
├── controllers/             # Camada de controle (API → Service)
├── services/               # Lógica de negócio e algoritmos
├── utils/                  # Utilitários e funções auxiliares
│   └── image_utils.py     # Funções de processamento de imagem
├── config.py              # Configurações da aplicação
├── main.py                # Entry point da API
└── requirements.txt       # Dependências do projeto
```

## 🛠️ Instalação

### Passos

1. Clone o repositório:
```bash
git clone <repository-url>
cd implementation
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🚀 Execução

Inicie o servidor de desenvolvimento:

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Acesse a documentação interativa (Swagger UI) em: `http://localhost:8000/docs`

## 📖 Uso da API

### Exemplo: Detecção de Bordas com Canny

```bash
curl -X POST "http://localhost:8000/canny/process" \
  -F "file=@image.png" \
  -F "sigma=1.0" \
  -F "low_threshold=0.1" \
  -F "high_threshold=0.3" \
  --output edges.png
```

### Exemplo: Contagem de Objetos

```bash
curl -X POST "http://localhost:8000/object-count/process" \
  -F "file=@image.png" \
  -F "threshold=128" \
  -F "method=ccl"
```

Resposta JSON:
```json
{
  "object_count": 5,
  "threshold_used": 128,
  "method": "connected_component_labeling"
}
```

### Exemplo: Freeman Chain Code

```bash
curl -X POST "http://localhost:8000/freeman-chain/process" \
  -F "file=@image.png" \
  -F "threshold=128"
```

Resposta JSON:
```json
{
  "total_contours": 2,
  "contours": [
    {
      "id": 1,
      "start_point": [10, 20],
      "chain_code": [0, 0, 1, 2, 3, 4, 4, 5, 6, 7],
      "length": 10
    }
  ]
}
```

## 🌐 Endpoints Disponíveis

| Endpoint | Método | Descrição | Parâmetros |
|----------|--------|-----------|------------|
| `/box-filter/process` | POST | Aplica filtro box (média) | `file`, `box_size` (default: 3) |
| `/canny/process` | POST | Detecção de bordas Canny | `file`, `sigma` (1.0), `low_threshold` (0.1), `high_threshold` (0.3) |
| `/marr-hildreth/process` | POST | Detecção de bordas Marr-Hildreth | `file`, `sigma` (1.0), `threshold` (0.1) |
| `/watershed/process` | POST | Segmentação Watershed | `file`, `gaussian_sigma` (1.0) |
| `/otsu-method/process` | POST | Limiarização de Otsu | `file` |
| `/segmentation/process` | POST | Segmentação por intensidade | `file` |
| `/freeman-chain/process` | POST | Código de cadeia Freeman | `file`, `threshold` (128) |
| `/object-count/process` | POST | Contagem de objetos | `file`, `threshold` (128), `method` ('ccl' ou 'freeman') |

## 🔬 Algoritmos Implementados

### 1. **Canny Edge Detection**
- Suavização Gaussiana
- Cálculo de gradiente (Sobel)
- Supressão não-máxima
- Histerese com dois thresholds

### 2. **Marr-Hildreth**
- Laplaciano da Gaussiana (LoG)
- Detecção de zero-crossing
- Threshold adaptativo

### 3. **Watershed Segmentation**
- Marcadores automáticos usando Otsu
- Transformada de distância
- Algoritmo de inundação de Meyer com fila de prioridade
- Detecção de linhas divisórias

### 4. **Freeman Chain Code**
- Traçamento de contorno 8-conectado
- Codificação direcional (0-7)
- Detecção de pixels de borda

### 5. **Connected Component Labeling (CCL)**
- Flood-fill iterativo
- Rotulagem 4-conectada
- Contagem de componentes

## 📚 Referências Técnicas e Científicas

### 1. Cadeia de Freeman (Freeman Chain Code)

**Artigo Original:**
- FREEMAN, H. *On the Encoding of Arbitrary Geometric Configurations*. IRE Transactions on Electronic Computers, vol. EC-10, no. 2, pp. 260-268, Jun. 1961. DOI: [10.1109/TEC.1961.5219197](https://doi.org/10.1109/TEC.1961.5219197)

**Notas de Aula (Teoria de Normalização e Invariância):**
- OJS Krede - University of Oslo: [INF4300 Notes](https://ojskrede.github.io/inf4300/notes/week_04/)
- EE NTHU - Digital Image Processing: [Chapter 11](https://www.ee.nthu.edu.tw/clhuang/09420EE368000DIP/chapter11.pdf)

**Repositórios e Implementações:**
- Kaggle - Freeman Chain Code Implementation: [Kaggle Notebook](https://www.kaggle.com/)
- GitHub - Simple Shape Recognition: [chaincode.py](https://github.com/)
- MathWorks - Shape Number & First Difference: [FileExchange](https://www.mathworks.com/matlabcentral/fileexchange/60017-freeman-chain-code-with-first-differences-and-shape-number)

### 2. Método de Otsu (Limiarização Global)

**Artigo Original:**
- OTSU, N. *A Threshold Selection Method from Gray-Level Histograms*. IEEE Transactions on Systems, Man, and Cybernetics, vol. 9, no. 1, pp. 62-66, Jan. 1979. DOI: [10.1109/TSMC.1979.4310076](https://doi.org/10.1109/TSMC.1979.4310076)

**Documentação Oficial:**
- OpenCV Python: [Thresholding Tutorial](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html)
- Scikit-image: [Thresholding Guide](https://scikit-image.org/docs/stable/auto_examples/applications/plot_thresholding_guide.html)

### 3. Rotulagem de Componentes Conectados (CCL)

**Artigo de Fundamentação:**
- ROSENFELD, A.; PFALTZ, J. L. *Sequential Operations in Digital Picture Processing*. Journal of the ACM, vol. 13, no. 4, pp. 471-494, Out. 1966. DOI: 10.1145/321356.321357

**Documentação e Teoria:**
- Wikipedia: [Connected-component labeling](https://en.wikipedia.org/wiki/Connected-component_labeling)
- OpenCV Python: [Shape Descriptors](https://docs.opencv.org/3.4/d3/dc0/group__imgproc__shape.html)
- Neubias Academy: [Connected Components](https://neubias.github.io/training-resources/connected_components/index.html)

### 4. Literatura de Referência Geral

**Livro Base:**
- GONZALEZ, R. C.; WOODS, R. E. *Digital Image Processing*. 4th Edition, Pearson Education, 2018.
- Site Oficial: [ImageProcessingPlace.com](http://www.imageprocessingplace.com/)

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos.
