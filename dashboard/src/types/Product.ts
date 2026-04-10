export interface Product {
  product_name: string;
  main_photo: string;
  asin: string;
  star_rating: number | null;
  review_count: number | null;
  sales_rank: string | null;
  price: string;
  direct_link: string;
}
