import { Component, OnInit } from '@angular/core';
import {FossService } from '../_service/foss.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public foss ;

  constructor(public apiService: FossService){
     this.foss = this.apiService.getFoss();
  }

  fossCategorySelected(category){
    console.log(category);
  }
  LanguageSelected(language){
    console.log(language);
  }
  
ngOnInit(){};
//   ngOnInit(){
//     this.apiService.getFoss().subscribe((res)=>{
//       this.apiService.getFoss().subscribe((res)=>{
//         console.log(res);
//       });      
//     });
// }

}
