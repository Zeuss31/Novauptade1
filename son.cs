namespace kdsakodsasda
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Bir pozitif tam sayı giriniz");
            int sayi = Convert.ToInt32(Console.ReadLine());

            int toplam = 0;
            for (int i = 1; i <= sayi; i++) 
            toplam += i;
            Console.WriteLine("1'den" + sayi + "'ya kadar olan sayıların toplamı: " + toplam);
        }
    }
}