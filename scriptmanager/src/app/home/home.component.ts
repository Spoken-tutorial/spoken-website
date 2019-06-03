import { Component, OnInit } from '@angular/core';
import { FossService } from '../_service/foss.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.sass']
})
export class HomeComponent implements OnInit {

  public foss ;

  constructor(public fossService: FossService){
  }

  fossCategorySelected(category){
    console.log(category);
  }
  LanguageSelected(language){
    console.log(language);
  }
  
  ngOnInit(){
    this.foss = this.fossService.getFoss().subscribe(
      (res) => this.foss = res,
      (err) => {
        console.log('Failed to fetch foss categories');
        console.error(err);
      }
    );
  };
}
