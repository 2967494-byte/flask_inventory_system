"""
Скрипт для удаления автоматически созданных товаров
Удаляет товары с маскированным телефоном "+X XXX XXX-XX-XX"
"""
from app import create_app, db
from app.models import Product
import os

def delete_generated_products():
    """Удаляет все автоматически сгенерированные товары"""
    app = create_app()
    
    with app.app_context():
        # Находим все товары с маскированным телефоном (признак автогенерации)
        generated_products = Product.query.filter_by(external_phone="+X XXX XXX-XX-XX").all()
        
        if not generated_products:
            print("Автоматически созданные товары не найдены.")
            return
        
        count = len(generated_products)
        print(f"Найдено {count} автоматически созданных товаров.")
        
        # Запрашиваем подтверждение
        confirm = input(f"Удалить все {count} товаров? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y', 'да', 'д']:
            print("Отменено.")
            return
        
        # Удаляем изображения
        upload_dir = app.config.get('UPLOAD_FOLDER', 'app/static/uploads')
        deleted_images = 0
        
        for product in generated_products:
            if product.images:
                for image_filename in product.images:
                    image_path = os.path.join(upload_dir, image_filename)
                    try:
                        if os.path.exists(image_path):
                            os.remove(image_path)
                            deleted_images += 1
                    except Exception as e:
                        print(f"Ошибка удаления изображения {image_filename}: {e}")
        
        # Удаляем товары из БД
        try:
            for product in generated_products:
                db.session.delete(product)
            
            db.session.commit()
            print(f"\n✓ Успешно удалено:")
            print(f"  - {count} товаров")
            print(f"  - {deleted_images} изображений")
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
            db.session.rollback()


if __name__ == "__main__":
    delete_generated_products()
