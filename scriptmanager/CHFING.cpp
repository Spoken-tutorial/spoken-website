#include<bits/stdc++.h>
using namespace std;
#define f(i,n) for(int i=0;i<n;i++)
#define ll long long int
#define m 1000000007
int main(){
	int t;
	cin>>t;
	while(t--){
		ll n1,k;
		cin>>n1>>k;

		ll min = k;
		ll max = k+n1-1;

		ll a = min*2 - max -1;
		ll d = -(max-min);
		// cout<<a<<" a "<<d<<" d "<<endl;
		if(a<=0){
			
			cout<<k-1<<endl;
			continue;
		}
	
		ll n = floor( (1-((float)a/d)) );
		// cout<<" n "<<n<<endl;
		// cout<<" d "<<d<<endl;
		ll ans;
		if(n%2==0){
			// cout<<(2*a-(n-1)*d)<<endl;
			ll t = ( (2*a)%m + ( ((n-1)%m)*(d%m) )%m )%m; 
			ans =  ( ((n/2)%m) * t%m )%m;
		}
		else{
			if(d%2==0)
					{
						ll t = ( (a)%m + ( ((n-1)%m)*((d/2)%m) )%m )%m;
						ans =  ( ((n)%m) * t%m )%m;
					}
			else
			{
				ll t = ( (a)%m + ( (( (n-1)/2 )%m)*(d%m) )%m )%m;
				ans =  ( ((n)%m) * t%m )%m;

			}
		}
		// cout<<ans<<" ans "<<endl;
		ans = ( (ans%m)+((k-1)%m) )%m;
		cout<<ans<<endl;
// 		// cout<<prod1<<endl;
		
// 		ll prod2 = ( (n-1)%m*(d%m) )%m;
		
			
// 		// cout<<prod2<<endl;
// 		ll prod3 = (prod1%m-prod2%m)%m;
// 		// cout<<prod3<<endl;
// 		prod3 = abs(prod3);
// 		ll prod4 = ( (n%m)*(prod3%m) )%m;
// 		prod4 = prod4/2;
// 		// cout<<prod4<<endl;
// 		ll prod5 = k-1;
// // cout<<prod5<<endl;
// 		ll prod6 = ( (prod5%m)+(prod4%m) )%m; 
// 		// cout<<prod6<<endl;

// 		cout<<prod6<<endl; 

	}

	// int a,d;
	// cin>>a>>d;

	// 	ll n = floor( (1-((float)a/d)) );
	// 	cout<<n;
	// 	cout<<LLONG_MAX<<endl;
	// 	cout<<LLONG_MIN<<endl;
}