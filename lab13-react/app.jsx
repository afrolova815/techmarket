const { useMemo, useState } = React;

const initialProducts = [
  {
    id: crypto.randomUUID(),
    name: 'iPhone 15 Pro',
    brand: 'Apple',
    category: 'Смартфоны',
    price: 129990,
    quantity: 5,
    isAvailable: true,
    created: new Date('2025-08-15').toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: 'Galaxy S24',
    brand: 'Samsung',
    category: 'Смартфоны',
    price: 99990,
    quantity: 12,
    isAvailable: true,
    created: new Date('2025-06-04').toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: 'MacBook Air M3',
    brand: 'Apple',
    category: 'Ноутбуки',
    price: 149990,
    quantity: 3,
    isAvailable: true,
    created: new Date('2025-07-20').toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: 'Dell XPS 13',
    brand: 'Dell',
    category: 'Ноутбуки',
    price: 139990,
    quantity: 7,
    isAvailable: true,
    created: new Date('2025-05-10').toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: 'Sony WH-1000XM5',
    brand: 'Sony',
    category: 'Аудио',
    price: 39990,
    quantity: 20,
    isAvailable: true,
    created: new Date('2025-04-01').toISOString(),
  },
  {
    id: crypto.randomUUID(),
    name: 'Apple Watch Series 10',
    brand: 'Apple',
    category: 'Гаджеты',
    price: 49990,
    quantity: 10,
    isAvailable: true,
    created: new Date('2025-09-01').toISOString(),
  },
];

function ProductItem({ product }) {
  return (
    <div className="product-item" role="listitem">
      <div className="product-head">
        <strong className="product-name">{product.name}</strong>
        <span className="product-brand"> · {product.brand}</span>
      </div>
      <div className="product-meta">
        <span className="product-category">{product.category}</span>
        <span className="product-price">{product.price.toLocaleString('ru-RU')} ₽</span>
      </div>
      <div className="product-info">
        <span>Количество: {product.quantity}</span>
        <span>Доступен: {product.isAvailable ? 'да' : 'нет'}</span>
        <span>Добавлен: {new Date(product.created).toLocaleDateString('ru-RU')}</span>
      </div>
    </div>
  );
}

function SortControls({ sortBy, setSortBy, sortDir, setSortDir }) {
  return (
    <div className="sort-controls">
      <label>
        Сортировать по:
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="name">Названию</option>
          <option value="price">Цене</option>
          <option value="created">Дате добавления</option>
        </select>
      </label>
      <label>
        Направление:
        <select
          value={sortDir}
          onChange={(e) => setSortDir(e.target.value)}
        >
          <option value="asc">По возрастанию</option>
          <option value="desc">По убыванию</option>
        </select>
      </label>
    </div>
  );
}

const initialForm = {
  name: '',
  brand: '',
  category: '',
  price: '',
  quantity: '',
  isAvailable: true,
};

function AddProductForm({ onAdd }) {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});

  const validate = () => {
    const next = {};
    if (!form.name || form.name.trim().length < 3) next.name = 'Минимум 3 символа';
    const priceNum = Number(form.price);
    if (!Number.isFinite(priceNum) || priceNum <= 0) next.price = 'Цена должна быть > 0';
    if (!form.category.trim()) next.category = 'Укажите категорию';
    if (!form.brand.trim()) next.brand = 'Укажите бренд';
    const qtyNum = Number(form.quantity);
    if (!Number.isInteger(qtyNum) || qtyNum < 0) next.quantity = 'Целое число ≥ 0';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const onSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    const newProduct = {
      id: crypto.randomUUID(),
      name: form.name.trim(),
      brand: form.brand.trim(),
      category: form.category.trim(),
      price: Number(form.price),
      quantity: Number(form.quantity),
      isAvailable: !!form.isAvailable,
      created: new Date().toISOString(),
    };
    onAdd(newProduct);
    setForm(initialForm);
    setErrors({});
  };

  const bind = (field) => ({
    value: form[field],
    onChange: (e) => setForm((s) => ({ ...s, [field]: e.target.value })),
    className: errors[field] ? 'invalid' : '',
  });

  return (
    <form className="add-form" onSubmit={onSubmit} noValidate>
      <h3>Добавить товар</h3>
      <div className="grid">
        <label>
          Название
          <input type="text" {...bind('name')} placeholder="Например, iPhone 15" />
          {errors.name && <small className="error">{errors.name}</small>}
        </label>
        <label>
          Бренд
          <input type="text" {...bind('brand')} placeholder="Apple" />
          {errors.brand && <small className="error">{errors.brand}</small>}
        </label>
        <label>
          Категория
          <input type="text" {...bind('category')} placeholder="Смартфоны" />
          {errors.category && <small className="error">{errors.category}</small>}
        </label>
        <label>
          Цена (₽)
          <input type="number" {...bind('price')} min="1" step="1" placeholder="49990" />
          {errors.price && <small className="error">{errors.price}</small>}
        </label>
        <label>
          Количество
          <input type="number" {...bind('quantity')} min="0" step="1" placeholder="10" />
          {errors.quantity && <small className="error">{errors.quantity}</small>}
        </label>
      </div>
      <label className="checkbox">
        <input
          type="checkbox"
          checked={!!form.isAvailable}
          onChange={(e) => setForm((s) => ({ ...s, isAvailable: e.target.checked }))}
        />
        Доступен к заказу
      </label>
      <div className="actions">
        <button type="submit">Добавить</button>
      </div>
    </form>
  );
}

function App() {
  const [products, setProducts] = useState(initialProducts);
  const [sortBy, setSortBy] = useState('name');
  const [sortDir, setSortDir] = useState('asc');
  const [success, setSuccess] = useState('');

  const sortedProducts = useMemo(() => {
    const dir = sortDir === 'asc' ? 1 : -1;
    const arr = [...products];
    arr.sort((a, b) => {
      let av = a[sortBy];
      let bv = b[sortBy];
      if (sortBy === 'name') {
        av = a.name.toLowerCase();
        bv = b.name.toLowerCase();
      }
      if (sortBy === 'created') {
        av = new Date(a.created).getTime();
        bv = new Date(b.created).getTime();
      }
      if (av < bv) return -1 * dir;
      if (av > bv) return 1 * dir;
      return 0;
    });
    return arr;
  }, [products, sortBy, sortDir]);

  const handleAdd = (p) => {
    setProducts((prev) => [p, ...prev]);
    setSuccess('Запись успешно добавлена');
    setTimeout(() => setSuccess(''), 2500);
  };

  return (
    <div className="layout">
      <div>
        <h2>Каталог товаров</h2>
        {success && <div className="alert alert-success" role="status">{success}</div>}
        <SortControls
          sortBy={sortBy}
          setSortBy={setSortBy}
          sortDir={sortDir}
          setSortDir={setSortDir}
        />
        <div className="product-list" role="list">
          {sortedProducts.map((p) => (
            <ProductItem key={p.id} product={p} />
          ))}
        </div>
      </div>
      <div>
        <AddProductForm onAdd={handleAdd} />
      </div>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
