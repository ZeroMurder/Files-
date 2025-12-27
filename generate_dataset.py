import json
import random
import re
from typing import List, Dict
from datetime import datetime

class ProfessionalQADataset:
    def __init__(self):
        self.categories = {
            "python": 0.25,
            "web_development": 0.20,
            "databases": 0.15,
            "devops": 0.15,
            "algorithms": 0.10,
            "frontend": 0.10,
            "backend": 0.05
        }
        
        self.base_questions = {
            "python": [
                ("Что такое list comprehension в Python?", 
                 "List comprehension — краткая форма создания списков: [x*2 for x in range(10)]. Эквивалентно for循环."),
                ("Как работает декоратор в Python?", 
                 "Декоратор — функция, оборачивающая другую функцию для расширения функциональности: @timer над def func()"),
                ("В чем разница между *args и **kwargs?", 
                 "*args — tuple переменных аргументов, **kwargs — dict именованных аргументов.")
            ],
            "web_development": [
                ("Что такое REST API?", 
                 "REST — архитектурный стиль для веб-сервисов: stateless, использует HTTP методы (GET/POST/PUT/DELETE)."),
                ("Как работает CORS?", 
                 "CORS (Cross-Origin Resource Sharing) — механизм браузера для безопасных кросс-доменных запросов."),
                ("Что такое JWT токен?", 
                 "JSON Web Token — компактный, самодостаточный токен для аутентификации: header.payload.signature.")
            ],
            "databases": [
                ("В чем разница между INNER JOIN и LEFT JOIN?", 
                 "INNER JOIN — только совпадающие записи, LEFT JOIN — все из левой таблицы + совпадающие из правой."),
                ("Что такое индекс в базе данных?", 
                 "Индекс ускоряет поиск, создавая структуру данных (B-tree) для быстрого доступа к записям."),
                ("Как оптимизировать медленный SQL запрос?", 
                 "EXPLAIN ANALYZE, добавление индексов, избегать SELECT *, лимитировать результаты.")
            ],
            "devops": [
                ("Что такое Docker контейнер?", 
                 "Контейнер — изолированная среда с приложением + зависимостями, используя ядро хоста."),
                ("Как работает CI/CD pipeline?", 
                 "Continuous Integration/Deployment: код → тест → build → deploy (GitHub Actions, Jenkins)."),
                ("В чем разница Docker и Kubernetes?", 
                 "Docker — контейнеризация, Kubernetes — оркестрация контейнеров в кластере.")
            ]
        }
    
    def generate_variations(self, question: str, answer: str, count: int = 8) -> List[Dict]:
        """Создает вариации для data augmentation"""
        variations = []
        templates = [
            question,
            question.lower(),
            f"Объясни: {question}",
            f"Расскажи про {re.sub(r'^(Что такое |Как )', '', question)}",
            f"Что значит {question.split(' ')[-1]}?"
        ]
        
        for i, template in enumerate(templates[:count]):
            variations.append({
                "question": template.strip(),
                "answer": answer,
                "category": self.categorize(template),
                "difficulty": min(i//2 + 1, 3),
                "tags": self.extract_tags(template)
            })
        return variations
    
    def categorize(self, question: str) -> str:
        """Автоматическая категоризация"""
        q = question.lower()
        for cat, questions in self.base_questions.items():
            for base_q, _ in questions:
                if any(word in q for word in base_q.lower().split()):
                    return cat
        return "general"
    
    def extract_tags(self, question: str) -> List[str]:
        """Извлекает ключевые слова"""
        words = re.findall(r'\b\w+\b', question.lower())
        return [w for w in words if len(w) > 3 and w not in ['что', 'как', 'это']]
    
    def generate_full_dataset(self, target_size: int = 1000) -> List[Dict]:
        """Генерирует профессиональный датасет"""
        dataset = []
        
        # Базовые вопросы с вариациями
        for category, qas in self.base_questions.items():
            for question, answer in qas:
                dataset.extend(self.generate_variations(question, answer, 12))
        
        # Дополнительная генерация
        while len(dataset) < target_size:
            category = random.choices(
                list(self.categories.keys()), 
                weights=list(self.categories.values())
            )[0]
            
            # Генерируем новый вопрос
            new_q, new_a = self.generate_dynamic_question(category)
            dataset.extend(self.generate_variations(new_q, new_a, 3))
        
        # Уникализация + shuffle
        seen = set()
        unique_dataset = []
        for item in random.sample(dataset, min(len(dataset), target_size*2)):
            if item["question"] not in seen:
                unique_dataset.append(item)
                seen.add(item["question"])
                if len(unique_dataset) >= target_size:
                    break
        
        return unique_dataset
    
    def generate_dynamic_question(self, category: str) -> tuple:
        """Динамическая генерация вопросов"""
        templates = {
            "python": [
                ("Как использовать context manager в Python?", 
                 "Context manager (with statement) автоматически управляет ресурсами: файлы, соединения БД."),
                ("Что такое generator в Python?", 
                 "Generator — функция с yield, возвращает итератор с ленивой оценкой.")
            ],
            "web_development": [
                ("Как оптимизировать загрузку сайта?", 
                 "Lazy loading изображений, minify CSS/JS, CDN, HTTP/2, кэширование."),
                ("Что такое SSR vs CSR?", 
                 "SSR (Server-Side Rendering) — HTML на сервере, CSR (Client-Side) — JS рендерит.")
            ]
        }
        return random.choice(templates.get(category, [("Общий вопрос?", "Общий ответ")]))
    
    def save_dataset(self, dataset: List[Dict], filename: str = "pro_qa_dataset.json"):
        """Сохраняет с метаданными"""
        metadata = {
            "created": datetime.now().isoformat(),
            "total_questions": len(dataset),
            "categories": {cat: 0 for cat in self.categories},
            "version": "2.0"
        }
        
        for item in dataset:
            metadata["categories"][item["category"]] += 1
        
        full_data = {
            "metadata": metadata,
            "data": dataset
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Датасет сохранен: {filename}")
        print(f"📊 Всего: {len(dataset)} вопросов")
        for cat, count in sorted(metadata["categories"].items(), key=lambda x: x[1], reverse=True):
            print(f"   {cat}: {count}")

def main():
    generator = ProfessionalQADataset()
    dataset = generator.generate_full_dataset(1000)
    generator.save_dataset(dataset)
    
    # Пример использования
    print("\n📖 Примеры вопросов:")
    for i, item in enumerate(dataset[:3]):
        print(f"{i+1}. {item['question']}")
        print(f"   → {item['category']} (сложность: {item['difficulty']})")

if __name__ == "__main__":
    main()
